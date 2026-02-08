"""Student memory management for tracking learning progress"""
import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class StudentMemory:
    """Manages student learning history and weak concepts"""
    
    def __init__(self, storage_file: str = "student_memory.json"):
        self.storage_file = Path(storage_file)
        self.memory: Dict[str, Dict] = {}
        self._load()
    
    def _load(self):
        """Load memory from file if exists"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.memory = json.load(f)
            except Exception:
                self.memory = {}
    
    def _save(self):
        """Save memory to file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save student memory: {e}")
    
    def update_after_test(self, student_id: str, test_id: str, topic: str, 
                         total_score: int, max_score: int, weak_concepts: List[str]):
        """
        Update student memory after test evaluation.
        
        Tracks:
        - Test history
        - Concept mastery
        - Weak areas
        - Progress over time
        """
        if student_id not in self.memory:
            self.memory[student_id] = {
                "student_id": student_id,
                "test_history": [],
                "concept_scores": defaultdict(list),
                "weak_concepts": set(),
                "total_tests": 0,
                "average_score": 0.0
            }
        
        student = self.memory[student_id]
        
        # Add test to history
        test_record = {
            "test_id": test_id,
            "topic": topic,
            "score": total_score,
            "max_score": max_score,
            "percentage": round((total_score / max_score * 100), 2) if max_score > 0 else 0,
            "timestamp": datetime.now().isoformat(),
            "weak_concepts": weak_concepts
        }
        
        if isinstance(student["test_history"], list):
            student["test_history"].append(test_record)
        else:
            student["test_history"] = [test_record]
        
        # Update weak concepts
        if isinstance(student.get("weak_concepts"), set):
            student["weak_concepts"] = list(student["weak_concepts"])
        
        current_weak = set(student.get("weak_concepts", []))
        current_weak.update(weak_concepts)
        student["weak_concepts"] = list(current_weak)
        
        # Update statistics
        student["total_tests"] = len(student["test_history"])
        
        # Calculate average score
        total_percentage = sum(t["percentage"] for t in student["test_history"])
        student["average_score"] = round(total_percentage / student["total_tests"], 2)
        
        self._save()
    
    def get_student_profile(self, student_id: str) -> Optional[Dict]:
        """Get complete student learning profile"""
        return self.memory.get(student_id)
    
    def get_weak_concepts(self, student_id: str) -> List[str]:
        """Get list of concepts student struggles with"""
        profile = self.get_student_profile(student_id)
        if not profile:
            return []
        return profile.get("weak_concepts", [])


# Global memory instance
_memory: Optional[StudentMemory] = None


def get_student_memory() -> StudentMemory:
    """Get or create global student memory instance"""
    global _memory
    if _memory is None:
        _memory = StudentMemory()
    return _memory
