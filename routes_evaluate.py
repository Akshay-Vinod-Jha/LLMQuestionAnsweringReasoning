"""Test evaluation route and scoring logic"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict
from schemas import (
    TestEvaluateRequest, TestEvaluateResponse,
    QuestionFeedback, LLMEvaluationResult, QuestionType
)
from llm_engine import call_llm
from prompts import get_evaluation_prompt, get_overall_feedback_prompt
from storage import get_storage
from student_memory import get_student_memory
from pydantic import ValidationError


router = APIRouter(prefix="/test", tags=["Test Evaluation"])


def evaluate_mcq(correct_answer: str, student_answer: str) -> bool:
    """Evaluate MCQ answer (exact match, case-insensitive)"""
    return correct_answer.strip().upper() == student_answer.strip().upper()


def calculate_rubric_score(accuracy: int, clarity: int, explanation: int, max_points: int) -> int:
    """
    Calculate points earned based on rubric scores.
    
    Rubric scoring:
    - Each dimension is 0-5
    - Total: 0-15 scale
    - Converted to question points (typically 10)
    """
    total_rubric = accuracy + clarity + explanation
    max_rubric = 15
    
    # Convert to percentage then to points
    percentage = (total_rubric / max_rubric) * 100
    points = int((percentage / 100) * max_points)
    
    return points


async def evaluate_single_question(question_data: dict, student_answer: str) -> QuestionFeedback:
    """
    Evaluate a single question answer.
    
    Returns detailed feedback with scores.
    """
    question_type = QuestionType(question_data["question_type"])
    correct_answer = question_data["correct_answer"]
    question_text = question_data["question_text"]
    explanation = question_data["explanation"]
    concept_tag = question_data["concept_tag"]
    points_possible = question_data["points"]
    
    if question_type == QuestionType.MCQ:
        # MCQ: Binary evaluation
        is_correct = evaluate_mcq(correct_answer, student_answer)
        points_earned = points_possible if is_correct else 0
        
        # Generate feedback via LLM
        prompt = get_evaluation_prompt(
            question_text=question_text,
            question_type="mcq",
            correct_answer=correct_answer,
            student_answer=student_answer,
            explanation=explanation,
            concept_tag=concept_tag
        )
        
        try:
            llm_response = call_llm(
                prompt=prompt,
                model="llama-3.1-8b-instant",
                temperature=0.2
            )
            feedback = llm_response.get("feedback", "Answer evaluated.")
        except Exception:
            feedback = f"Your answer is {'correct' if is_correct else 'incorrect'}. {explanation}"
        
        return QuestionFeedback(
            question_id=question_data["question_id"],
            question_type=question_type,
            student_answer=student_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            points_earned=points_earned,
            points_possible=points_possible,
            feedback=feedback,
            concept_tag=concept_tag
        )
    
    else:
        # Short answer or numerical: Rubric-based evaluation
        prompt = get_evaluation_prompt(
            question_text=question_text,
            question_type=question_type.value,
            correct_answer=correct_answer,
            student_answer=student_answer,
            explanation=explanation,
            concept_tag=concept_tag
        )
        
        try:
            llm_response = call_llm(
                prompt=prompt,
                model="llama-3.1-8b-instant",
                temperature=0.2
            )
            
            # Validate response
            eval_result = LLMEvaluationResult(**llm_response)
        except ValidationError as e:
            raise HTTPException(
                status_code=500,
                detail=f"LLM evaluation response validation failed: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Question evaluation failed: {str(e)}"
            )
        
        # Calculate points
        points_earned = calculate_rubric_score(
            accuracy=eval_result.accuracy_score,
            clarity=eval_result.clarity_score,
            explanation=eval_result.explanation_score,
            max_points=points_possible
        )
        
        return QuestionFeedback(
            question_id=question_data["question_id"],
            question_type=question_type,
            student_answer=student_answer,
            correct_answer=correct_answer,
            accuracy_score=eval_result.accuracy_score,
            clarity_score=eval_result.clarity_score,
            explanation_score=eval_result.explanation_score,
            points_earned=points_earned,
            points_possible=points_possible,
            feedback=eval_result.feedback,
            concept_tag=concept_tag
        )


@router.post("/evaluate", response_model=TestEvaluateResponse)
async def evaluate_test(request: TestEvaluateRequest):
    """
    Evaluate student's test answers using rubric-based scoring.
    
    Returns:
        - Individual question feedback with scores
        - Total score and percentage
        - Weak concepts identified
        - Personalized improvement suggestions
        - Updates student memory
    """
    try:
        # Retrieve test data
        storage = get_storage()
        test_data = storage.get_test(request.test_id)
        
        if not test_data:
            raise HTTPException(
                status_code=404,
                detail=f"Test {request.test_id} not found"
            )
        
        # Create answer lookup
        answer_map: Dict[str, str] = {
            ans.question_id: ans.answer 
            for ans in request.student_answers
        }
        
        # Evaluate each question
        question_feedback: List[QuestionFeedback] = []
        total_score = 0
        max_score = 0
        weak_concepts: List[str] = []
        
        for question_data in test_data["questions"]:
            question_id = question_data["question_id"]
            student_answer = answer_map.get(question_id, "")
            
            if not student_answer:
                # No answer provided
                feedback = QuestionFeedback(
                    question_id=question_id,
                    question_type=QuestionType(question_data["question_type"]),
                    student_answer="",
                    correct_answer=question_data["correct_answer"],
                    points_earned=0,
                    points_possible=question_data["points"],
                    feedback="No answer provided.",
                    concept_tag=question_data["concept_tag"]
                )
                weak_concepts.append(question_data["concept_tag"])
            else:
                # Evaluate answer
                feedback = await evaluate_single_question(question_data, student_answer)
                
                # Track weak concepts (low scores)
                if feedback.question_type == QuestionType.MCQ:
                    if not feedback.is_correct:
                        weak_concepts.append(feedback.concept_tag)
                else:
                    # For rubric-based, consider weak if avg score < 3
                    avg_score = (
                        (feedback.accuracy_score or 0) + 
                        (feedback.clarity_score or 0) + 
                        (feedback.explanation_score or 0)
                    ) / 3
                    if avg_score < 3:
                        weak_concepts.append(feedback.concept_tag)
            
            question_feedback.append(feedback)
            total_score += feedback.points_earned
            max_score += feedback.points_possible
        
        # Calculate percentage
        percentage = round((total_score / max_score * 100), 2) if max_score > 0 else 0
        
        # Remove duplicate weak concepts
        weak_concepts = list(set(weak_concepts))
        
        # Generate overall feedback and suggestions via LLM
        try:
            overall_prompt = get_overall_feedback_prompt(weak_concepts, percentage)
            overall_response = call_llm(
                prompt=overall_prompt,
                model="llama-3.1-8b-instant",
                temperature=0.3
            )
        except Exception:
            overall_response = {}
        
        improvement_suggestions = overall_response.get("improvement_suggestions", [
            "Review the concepts you missed",
            "Practice more questions on weak topics",
            "Seek help from instructor on difficult areas"
        ])
        overall_feedback = overall_response.get("overall_feedback", 
            f"You scored {percentage:.1f}%. Keep practicing to improve!")
        
        # Fallback feedback if models fail
        if not improvement_suggestions or not overall_feedback:
            # Fallback feedback
            improvement_suggestions = [
                f"Focus on improving: {', '.join(weak_concepts[:3])}" if weak_concepts else "Continue practicing",
                "Review explanations for incorrect answers",
                "Try more practice tests to strengthen understanding"
            ]
            overall_feedback = f"Test completed with {percentage:.1f}% score. Review the feedback for each question."
        
        # Update student memory
        student_id = "default_student"  # In production, get from auth context
        memory = get_student_memory()
        memory.update_after_test(
            student_id=student_id,
            test_id=request.test_id,
            topic=test_data["topic"],
            total_score=total_score,
            max_score=max_score,
            weak_concepts=weak_concepts
        )
        
        return TestEvaluateResponse(
            test_id=request.test_id,
            total_score=total_score,
            max_score=max_score,
            percentage=percentage,
            question_feedback=question_feedback,
            weak_concepts=weak_concepts,
            improvement_suggestions=improvement_suggestions,
            overall_feedback=overall_feedback
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Test evaluation failed: {str(e)}"
        )
