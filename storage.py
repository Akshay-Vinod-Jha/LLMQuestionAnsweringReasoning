"""Test storage and management"""
import json
from typing import Dict, Optional
from pathlib import Path
from schemas import QuestionInternal


class TestStorage:
    """Simple in-memory test storage with file persistence"""
    
    def __init__(self, storage_file: str = "test_storage.json"):
        self.storage_file = Path(storage_file)
        self.tests: Dict[str, Dict] = {}
        self._load()
    
    def _load(self):
        """Load tests from file if exists"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.tests = json.load(f)
            except Exception:
                self.tests = {}
    
    def _save(self):
        """Save tests to file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.tests, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save tests to file: {e}")
    
    def store_test(self, test_id: str, questions: list, topic: str, difficulty: str):
        """Store a generated test with internal data"""
        self.tests[test_id] = {
            "test_id": test_id,
            "topic": topic,
            "difficulty": difficulty,
            "questions": [q.dict() if hasattr(q, 'dict') else q for q in questions]
        }
        self._save()
    
    def get_test(self, test_id: str) -> Optional[Dict]:
        """Retrieve a test by ID"""
        return self.tests.get(test_id)
    
    def get_question(self, test_id: str, question_id: str) -> Optional[QuestionInternal]:
        """Get a specific question from a test"""
        test = self.get_test(test_id)
        if not test:
            return None
        
        for q in test["questions"]:
            if q["question_id"] == question_id:
                return QuestionInternal(**q)
        return None


# Global storage instance
_storage: Optional[TestStorage] = None


def get_storage() -> TestStorage:
    """Get or create global storage instance"""
    global _storage
    if _storage is None:
        _storage = TestStorage()
    return _storage
