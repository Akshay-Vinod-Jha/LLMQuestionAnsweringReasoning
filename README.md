# Auto Test Generator & Evaluator

## Feature-9: AI-Powered Test Generation & Evaluation

Production-ready backend for generating educational tests and evaluating student answers using Groq Cloud API.

---

## Architecture

```
backend/
├── main.py                 # FastAPI application entry point
├── schemas.py              # Pydantic models & validation
├── llm_engine.py          # Groq API integration
├── prompts.py             # LLM prompt templates
├── routes_generate.py     # Test generation endpoint
├── routes_evaluate.py     # Test evaluation endpoint
├── storage.py             # Test storage management
├── student_memory.py      # Learning progress tracking
├── requirements.txt       # Python dependencies
└── .env.example          # Environment configuration template
```

---

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Groq API key
GROQ_API_KEY=your_actual_groq_api_key
```

### 3. Run Server

```bash
python main.py
```

Server starts at: `http://localhost:8000`

---

## API Endpoints

### Generate Test

**POST** `/test/generate`

**Request:**

```json
{
  "topic": "Python Data Structures",
  "difficulty": "medium",
  "number_of_questions": 5,
  "question_types": ["mcq", "short", "numerical"]
}
```

**Response:**

```json
{
  "test_id": "test_abc123def456",
  "questions": [
    {
      "question_id": "q1",
      "question_text": "What is the time complexity of accessing an element in a Python list?",
      "question_type": "mcq",
      "mcq_options": [
        { "option": "O(1)", "label": "A" },
        { "option": "O(n)", "label": "B" },
        { "option": "O(log n)", "label": "C" },
        { "option": "O(n²)", "label": "D" }
      ],
      "points": 10
    }
  ],
  "total_points": 50,
  "topic": "Python Data Structures",
  "difficulty": "medium"
}
```

### Evaluate Test

**POST** `/test/evaluate`

**Request:**

```json
{
  "test_id": "test_abc123def456",
  "student_answers": [
    {
      "question_id": "q1",
      "answer": "A"
    },
    {
      "question_id": "q2",
      "answer": "A list is a mutable, ordered collection..."
    }
  ]
}
```

**Response:**

```json
{
  "test_id": "test_abc123def456",
  "total_score": 42,
  "max_score": 50,
  "percentage": 84.0,
  "question_feedback": [
    {
      "question_id": "q1",
      "question_type": "mcq",
      "student_answer": "A",
      "correct_answer": "A",
      "is_correct": true,
      "points_earned": 10,
      "points_possible": 10,
      "feedback": "Correct! List access is O(1)...",
      "concept_tag": "time_complexity"
    },
    {
      "question_id": "q2",
      "question_type": "short",
      "student_answer": "A list is...",
      "correct_answer": "Expected answer...",
      "accuracy_score": 4,
      "clarity_score": 5,
      "explanation_score": 4,
      "points_earned": 8,
      "points_possible": 10,
      "feedback": "Good explanation with minor gaps...",
      "concept_tag": "data_structures"
    }
  ],
  "weak_concepts": ["algorithm_analysis"],
  "improvement_suggestions": [
    "Review algorithm complexity analysis",
    "Practice more numerical problems",
    "Study edge cases in data structures"
  ],
  "overall_feedback": "Strong performance! Focus on algorithm analysis to reach mastery."
}
```

---

## LLM Integration

### Models Used

- **Generation**: `llama-3.1-8b-instant` (question generation)
- **Evaluation**: `llama-3.1-8b-instant` (answer assessment)

### Prompt Engineering

- **Deterministic**: Temperature ≤ 0.3
- **Structured**: Strict JSON output only
- **Validated**: Pydantic schema enforcement
- **Resilient**: Automatic retry on malformed responses

---

## Evaluation Rubric

### MCQ Questions

- Binary scoring: Correct = 100%, Incorrect = 0%
- AI-generated contextual feedback

### Short Answer & Numerical

Scored on 0-5 scale across 3 dimensions:

1. **Accuracy** (0-5): Correctness of answer
2. **Conceptual Clarity** (0-5): Understanding demonstrated
3. **Explanation Quality** (0-5): Communication effectiveness

**Points Calculation:**

```
Total Rubric Score = Accuracy + Clarity + Explanation (0-15)
Percentage = (Total / 15) × 100
Points Earned = (Percentage / 100) × Question Points
```

---

## Student Memory

Automatically tracks:

- Test history & scores
- Weak concept identification
- Progress trends
- Personalized recommendations

Updated after each test evaluation.

---

## Error Handling

- **Validation**: Pydantic schemas catch invalid inputs
- **LLM Failures**: Automatic retry with enhanced prompts
- **Missing Data**: Graceful fallbacks with informative errors
- **API Errors**: Proper HTTP status codes & messages

---

## Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### Generate Sample Test

```bash
curl -X POST http://localhost:8000/test/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Machine Learning Basics",
    "difficulty": "easy",
    "number_of_questions": 3,
    "question_types": ["mcq", "short"]
  }'
```

---

## Production Considerations

1. **Authentication**: Add user authentication (JWT, OAuth)
2. **Database**: Replace file storage with PostgreSQL/MongoDB
3. **Rate Limiting**: Implement API rate limits
4. **Caching**: Cache LLM responses for identical prompts
5. **Monitoring**: Add logging, metrics, error tracking
6. **CORS**: Configure specific allowed origins

---

## Dependencies

- **FastAPI**: Modern, high-performance web framework
- **Groq**: Official Groq Cloud API client
- **Pydantic**: Data validation & schema enforcement
- **Uvicorn**: ASGI server for production deployment

---

## License

Built for AI-Powered Multimodal Smart Learning Assistant Hackathon Project.
