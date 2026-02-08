"""Test generation route and logic"""
from fastapi import APIRouter, HTTPException
from typing import List
import uuid
import os
from schemas import (
    TestGenerateRequest, TestGenerateResponse,
    QuestionInternal, QuestionPublic, LLMQuestionGeneration
)
from llm_engine import call_llm
from prompts import get_question_generation_prompt
from storage import get_storage
from pydantic import ValidationError


router = APIRouter(prefix="/test", tags=["Test Generation"])


@router.post("/generate", response_model=TestGenerateResponse)
async def generate_test(request: TestGenerateRequest):
    """
    Generate a test with specified parameters.
    
    Returns:
        - test_id: Unique identifier for the test
        - questions: List of questions WITHOUT correct answers
        - total_points: Sum of all question points
    
    Internal:
        - Stores questions WITH correct answers for later evaluation
    """
    try:
        # Generate unique test ID
        test_id = f"test_{uuid.uuid4().hex[:12]}"
        
        # Prepare LLM prompt
        question_types = [qt.value for qt in request.question_types]
        prompt = get_question_generation_prompt(
            topic=request.topic,
            difficulty=request.difficulty.value,
            num_questions=request.number_of_questions,
            question_types=question_types
        )
        
        # Call LLM for question generation
        llm_response = call_llm(
            prompt=prompt,
            model=os.getenv("GENERATION_MODEL", "llama-3.1-8b-instant"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.3"))
        )
        
        # Validate LLM response structure
        try:
            llm_data = LLMQuestionGeneration(**llm_response)
        except ValidationError as e:
            raise HTTPException(
                status_code=500,
                detail=f"LLM returned invalid question format: {str(e)}"
            )
        
        # Ensure we got the requested number of questions
        if len(llm_data.questions) != request.number_of_questions:
            raise HTTPException(
                status_code=500,
                detail=f"LLM generated {len(llm_data.questions)} questions, expected {request.number_of_questions}"
            )
        
        # Store internal questions (with correct answers)
        internal_questions: List[QuestionInternal] = llm_data.questions
        storage = get_storage()
        storage.store_test(
            test_id=test_id,
            questions=internal_questions,
            topic=request.topic,
            difficulty=request.difficulty.value
        )
        
        # Create public questions (without correct answers)
        public_questions: List[QuestionPublic] = []
        total_points = 0
        
        for q in internal_questions:
            public_q = QuestionPublic(
                question_id=q.question_id,
                question_text=q.question_text,
                question_type=q.question_type,
                mcq_options=q.mcq_options,
                points=q.points
            )
            public_questions.append(public_q)
            total_points += q.points
        
        # Return response without correct answers
        return TestGenerateResponse(
            test_id=test_id,
            questions=public_questions,
            total_points=total_points,
            topic=request.topic,
            difficulty=request.difficulty
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Test generation failed: {str(e)}"
        )
