"""Pydantic schemas for test generation and evaluation"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum


class QuestionType(str, Enum):
    MCQ = "mcq"
    SHORT = "short"
    NUMERICAL = "numerical"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# ===== Test Generation Schemas =====

class TestGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="Topic for test generation")
    difficulty: Difficulty = Field(..., description="Difficulty level")
    number_of_questions: int = Field(..., ge=1, le=20, description="Number of questions")
    question_types: List[QuestionType] = Field(..., min_items=1, description="Types of questions")


class MCQOption(BaseModel):
    option: str
    label: str  # A, B, C, D


class QuestionInternal(BaseModel):
    """Internal question structure with correct answers"""
    question_id: str
    question_text: str
    question_type: QuestionType
    mcq_options: Optional[List[MCQOption]] = None
    correct_answer: str
    explanation: str = Field(default="No explanation provided")
    concept_tag: str = Field(default="general")
    points: int = 10


class QuestionPublic(BaseModel):
    """Public question structure without correct answers"""
    question_id: str
    question_text: str
    question_type: QuestionType
    mcq_options: Optional[List[MCQOption]] = None
    points: int = 10


class TestGenerateResponse(BaseModel):
    test_id: str
    questions: List[QuestionPublic]
    total_points: int
    topic: str
    difficulty: Difficulty


# ===== Test Evaluation Schemas =====

class StudentAnswer(BaseModel):
    question_id: str
    answer: str


class TestEvaluateRequest(BaseModel):
    test_id: str
    student_answers: List[StudentAnswer]


class QuestionFeedback(BaseModel):
    question_id: str
    question_type: QuestionType
    student_answer: str
    correct_answer: str
    is_correct: Optional[bool] = None  # For MCQ
    accuracy_score: Optional[int] = None  # 0-5 for short/numerical
    clarity_score: Optional[int] = None  # 0-5 for short/numerical
    explanation_score: Optional[int] = None  # 0-5 for short/numerical
    points_earned: int
    points_possible: int
    feedback: str
    concept_tag: str


class TestEvaluateResponse(BaseModel):
    test_id: str
    total_score: int
    max_score: int
    percentage: float
    question_feedback: List[QuestionFeedback]
    weak_concepts: List[str]
    improvement_suggestions: List[str]
    overall_feedback: str


# ===== LLM Response Schemas =====

class LLMQuestionGeneration(BaseModel):
    """Expected structure from LLM for question generation"""
    questions: List[QuestionInternal]


class LLMEvaluationResult(BaseModel):
    """Expected structure from LLM for evaluation"""
    accuracy_score: int = Field(..., ge=0, le=5)
    clarity_score: int = Field(..., ge=0, le=5)
    explanation_score: int = Field(..., ge=0, le=5)
    feedback: str
    is_conceptually_correct: bool
