"""
Example usage and testing script for Auto Test Generator & Evaluator
Run this after starting the FastAPI server
"""
import requests
import json


BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test health check endpoint"""
    print("=" * 60)
    print("Testing Health Check...")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_generate_test():
    """Test test generation"""
    print("=" * 60)
    print("Testing Test Generation...")
    print("=" * 60)
    
    payload = {
        "topic": "Python Programming Basics",
        "difficulty": "medium",
        "number_of_questions": 3,
        "question_types": ["mcq", "short", "numerical"]
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    print()
    
    response = requests.post(f"{BASE_URL}/test/generate", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Test ID: {data['test_id']}")
        print(f"Total Points: {data['total_points']}")
        print(f"Number of Questions: {len(data['questions'])}")
        print()
        
        for i, q in enumerate(data['questions'], 1):
            print(f"Question {i}:")
            print(f"  Type: {q['question_type']}")
            print(f"  Text: {q['question_text'][:80]}...")
            print(f"  Points: {q['points']}")
            print()
        
        return data['test_id'], data['questions']
    else:
        print(f"Error: {response.text}")
        return None, None


def test_evaluate_test(test_id: str, questions: list):
    """Test test evaluation"""
    print("=" * 60)
    print("Testing Test Evaluation...")
    print("=" * 60)
    
    # Create sample answers
    student_answers = []
    for q in questions:
        if q['question_type'] == 'mcq':
            # Pick first option for MCQ
            answer = q['mcq_options'][0]['label'] if q['mcq_options'] else 'A'
        elif q['question_type'] == 'short':
            answer = "This is a sample short answer demonstrating understanding of the concept."
        else:  # numerical
            answer = "42"
        
        student_answers.append({
            "question_id": q['question_id'],
            "answer": answer
        })
    
    payload = {
        "test_id": test_id,
        "student_answers": student_answers
    }
    
    print(f"Request: Evaluating {len(student_answers)} answers")
    print()
    
    response = requests.post(f"{BASE_URL}/test/evaluate", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total Score: {data['total_score']}/{data['max_score']}")
        print(f"Percentage: {data['percentage']}%")
        print()
        
        print("Question Feedback:")
        for fb in data['question_feedback']:
            print(f"\n  Question {fb['question_id']} ({fb['question_type']}):")
            print(f"    Points: {fb['points_earned']}/{fb['points_possible']}")
            
            if fb['question_type'] == 'mcq':
                print(f"    Correct: {fb['is_correct']}")
            else:
                print(f"    Accuracy: {fb['accuracy_score']}/5")
                print(f"    Clarity: {fb['clarity_score']}/5")
                print(f"    Explanation: {fb['explanation_score']}/5")
            
            print(f"    Feedback: {fb['feedback'][:100]}...")
        
        print(f"\nWeak Concepts: {', '.join(data['weak_concepts']) if data['weak_concepts'] else 'None'}")
        print(f"\nImprovement Suggestions:")
        for suggestion in data['improvement_suggestions']:
            print(f"  - {suggestion}")
        
        print(f"\nOverall Feedback: {data['overall_feedback']}")
    else:
        print(f"Error: {response.text}")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AUTO TEST GENERATOR & EVALUATOR - TESTING SUITE")
    print("=" * 60 + "\n")
    
    try:
        # Test 1: Health check
        test_health_check()
        
        # Test 2: Generate test
        test_id, questions = test_generate_test()
        
        if test_id and questions:
            # Test 3: Evaluate test
            test_evaluate_test(test_id, questions)
        
        print("\n" + "=" * 60)
        print("TESTING COMPLETE")
        print("=" * 60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server.")
        print("Make sure the FastAPI server is running:")
        print("  cd backend")
        print("  python main.py")
        print()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
