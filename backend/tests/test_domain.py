import unittest
from backend.domain.entities import Student
from backend.domain.value_objects import RecognitionResult

class TestDomainBoundaries(unittest.TestCase):
    
    def test_student_entity_initialization(self):
        """Verify Student entity initializes purely without DB hooks."""
        student = Student(
            student_id="uuid-123",
            institution_id="ORG1",
            name="John Doe",
            roll_number="A01",
            gender="M",
            embedding=[0.1, 0.2, 0.3]
        )
        self.assertEqual(student.name, "John Doe")
        self.assertEqual(len(student.embedding), 3)

    def test_recognition_result_logic(self):
        """Test Value Object formatting structure is enforced."""
        result = RecognitionResult(
            student_id="uuid-123",
            name="John Doe",
            confidence=0.95,
            status="mark",
            box=[1, 2, 3, 4],
            frames_tracked=5,
            frames_needed=4
        )
        self.assertTrue(result.confidence > 0.90)
        self.assertEqual(result.status, "mark")

if __name__ == '__main__':
    unittest.main()
