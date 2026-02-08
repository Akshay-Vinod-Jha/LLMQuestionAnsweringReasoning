"""Prompt templates for test generation and evaluation"""


def get_question_generation_prompt(topic: str, difficulty: str, num_questions: int, question_types: list) -> str:
    """
    Generate prompt for test question generation.
    
    Returns deterministic, structured prompt for LLM.
    """
    types_str = ", ".join(question_types)
    
    prompt = f"""Generate exactly {num_questions} test questions on the topic: "{topic}".

Difficulty level: {difficulty}
Question types to include: {types_str}

STRICT REQUIREMENTS:
1. Generate diverse questions covering different aspects of the topic
2. Each question must be clear, unambiguous, and educational
3. For MCQ questions: provide 4 options labeled A, B, C, D
4. For short answer: expect 2-4 sentence responses
5. For numerical: expect numeric answers with units if applicable
6. Difficulty must match: {difficulty}
   - easy: basic recall and understanding
   - medium: application and analysis
   - hard: synthesis and evaluation
7. Each question worth 10 points
8. MANDATORY: Every question MUST include "explanation" and "concept_tag" fields

OUTPUT FORMAT (JSON only):
{{
    "questions": [
        {{
            "question_id": "q1",
            "question_text": "What is...",
            "question_type": "mcq",
            "mcq_options": [
                {{"option": "Choice A", "label": "A"}},
                {{"option": "Choice B", "label": "B"}},
                {{"option": "Choice C", "label": "C"}},
                {{"option": "Choice D", "label": "D"}}
            ],
            "correct_answer": "A",
            "explanation": "Detailed explanation of why this is correct and what concept it tests",
            "concept_tag": "main_concept_being_tested",
            "points": 10
        }},
        {{
            "question_id": "q2",
            "question_text": "Explain...",
            "question_type": "short",
            "mcq_options": null,
            "correct_answer": "Expected answer content...",
            "explanation": "What a good answer should include and why",
            "concept_tag": "specific_concept_name",
            "points": 10
        }},
        {{
            "question_id": "q3",
            "question_text": "Calculate...",
            "question_type": "numerical",
            "mcq_options": null,
            "correct_answer": "42.5 meters",
            "explanation": "Step-by-step calculation and reasoning behind the answer",
            "concept_tag": "specific_concept_name",
            "points": 10
        }}
    ]
}}

Return ONLY the JSON. No markdown, no explanations, no code blocks."""
    
    return prompt


def get_evaluation_prompt(question_text: str, question_type: str, correct_answer: str, 
                          student_answer: str, explanation: str, concept_tag: str) -> str:
    """
    Generate prompt for evaluating a student's answer.
    
    Returns structured evaluation prompt with rubric.
    """
    
    if question_type == "mcq":
        # MCQ evaluation is binary, but we still generate feedback
        prompt = f"""Evaluate this multiple-choice question answer.

Question: {question_text}
Correct Answer: {correct_answer}
Student Answer: {student_answer}
Explanation: {explanation}
Concept: {concept_tag}

Since this is MCQ, evaluate if the student's answer matches the correct answer exactly.

OUTPUT FORMAT (JSON only):
{{
    "is_correct": true or false,
    "feedback": "Brief feedback explaining why the answer is correct/incorrect and what concept it tests"
}}

Return ONLY the JSON. No markdown, no explanations."""
        
    else:
        # Short answer or numerical - use rubric
        prompt = f"""Evaluate this {"short answer" if question_type == "short" else "numerical"} question response using a strict rubric.

Question: {question_text}
Correct/Expected Answer: {correct_answer}
Student Answer: {student_answer}
Explanation: {explanation}
Concept: {concept_tag}

EVALUATION RUBRIC (0-5 scale for each):

1. ACCURACY (0-5):
   - 5: Perfectly accurate, all key points correct
   - 4: Mostly accurate, minor errors
   - 3: Partially accurate, some key points missing
   - 2: Significant inaccuracies
   - 1: Mostly incorrect
   - 0: Completely wrong or no answer

2. CONCEPTUAL CLARITY (0-5):
   - 5: Demonstrates deep understanding of concept
   - 4: Good understanding, well explained
   - 3: Basic understanding shown
   - 2: Vague or confused understanding
   - 1: Minimal understanding
   - 0: No understanding demonstrated

3. EXPLANATION QUALITY (0-5):
   - 5: Clear, logical, well-structured explanation
   - 4: Good explanation with minor gaps
   - 3: Adequate explanation
   - 2: Poorly structured or incomplete
   - 1: Minimal explanation
   - 0: No explanation or incomprehensible

OUTPUT FORMAT (JSON only):
{{
    "accuracy_score": 0-5,
    "clarity_score": 0-5,
    "explanation_score": 0-5,
    "feedback": "Detailed feedback explaining the scores and what the student did well or needs to improve. Be specific and constructive.",
    "is_conceptually_correct": true or false (overall assessment)
}}

Return ONLY the JSON. No markdown, no explanations, no code blocks."""
    
    return prompt


def get_overall_feedback_prompt(weak_concepts: list, total_percentage: float) -> str:
    """Generate overall performance feedback"""
    
    weak_concepts_str = ", ".join(weak_concepts) if weak_concepts else "none identified"
    
    prompt = f"""Generate personalized overall feedback for a student's test performance.

Total Score: {total_percentage:.1f}%
Weak Concepts: {weak_concepts_str}

Provide:
1. Overall assessment of performance
2. Specific areas needing improvement
3. 2-3 actionable study suggestions

Keep feedback encouraging but honest. Focus on growth mindset.

OUTPUT FORMAT (JSON only):
{{
    "improvement_suggestions": [
        "Specific suggestion 1",
        "Specific suggestion 2",
        "Specific suggestion 3"
    ],
    "overall_feedback": "Brief overall assessment and encouragement (2-3 sentences)"
}}

Return ONLY the JSON. No markdown, no code blocks."""
    
    return prompt
