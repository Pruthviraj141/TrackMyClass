import base64
from io import BytesIO
from PIL import Image

from backend.core.errors import ValidationError
from backend.repositories.student_repository import StudentRepository
from backend.ml.detector.face_detection import detect_single_face
from backend.ml.embedding.embedding_service import generate_average_embedding
from backend.domain.entities import Student
from backend.core.config import MAX_FRAME_SIZE_BYTES, MIN_FRAMES_REQUIRED
from backend.core.security import get_password_hash
import uuid

class RegistrationService:
    def __init__(self, institution_id: str):
        self.institution_id = institution_id
        self.student_repo = StudentRepository()

    def register_student(self, name: str, roll_number: str, frames: list, gender: str = "unknown", password: str = None):
        if not frames or len(frames) < MIN_FRAMES_REQUIRED:
            raise ValidationError(f"At least {MIN_FRAMES_REQUIRED} frames are required")

        face_tensors = []
        for i, frame in enumerate(frames):
            try:
                frame_bytes = base64.b64decode(frame)
                if len(frame_bytes) > MAX_FRAME_SIZE_BYTES:
                    raise ValidationError(f"Frame {i} exceeds max size")
                image = Image.open(BytesIO(frame_bytes)).convert("RGB")
            except Exception as e:
                raise ValidationError(f"Invalid frame format: {e}")

            tensor = detect_single_face(image)
            if tensor is None:
                continue
            face_tensors.append(tensor.face_crop_tensor)

        if len(face_tensors) < MIN_FRAMES_REQUIRED:
            raise ValidationError("Not enough recognizable faces found.")

        try:
            # We bypass RecognitionEngine here as this is direct average embedding profiling,
            # rather than multi-face matching.
            final_embedding = generate_average_embedding(face_tensors)
        except Exception as e:
            raise ValidationError("Failed to build facial profile")

        # Convert back to standard array for DB storage
        emb_list = final_embedding.vector.tolist()
        
        hashed_pw = get_password_hash(password) if password else None

        student = Student(
            student_id=str(uuid.uuid4()),
            institution_id=self.institution_id,
            name=name,
            roll_number=roll_number,
            gender=gender,
            embedding=emb_list,
            password=hashed_pw
        )

        success = self.student_repo.add(student)
        if not success:
            raise ValidationError("Database constraint failure during registration")

        # Reload cache to accept new student
        from backend.ml.matcher.optimized_recognition import get_embedding_cache
        from backend.core.config import REDIS_URL
        import redis
        
        cache = get_embedding_cache()
        cache.refresh(self.institution_id)

        try:
            r = redis.Redis.from_url(REDIS_URL)
            r.publish("cache:invalidation", self.institution_id)
        except Exception as e:
            print(f"Failed to publish invalidation: {e}")

        return student.student_id

    def update_student_embedding(self, student_id: str, frames: list):
        if not frames or len(frames) < MIN_FRAMES_REQUIRED:
            raise ValidationError(f"At least {MIN_FRAMES_REQUIRED} frames are required")

        face_tensors = []
        for i, frame in enumerate(frames):
            try:
                frame_bytes = base64.b64decode(frame)
                if len(frame_bytes) > MAX_FRAME_SIZE_BYTES:
                    raise ValidationError(f"Frame {i} exceeds max size")
                image = Image.open(BytesIO(frame_bytes)).convert("RGB")
            except Exception as e:
                raise ValidationError(f"Invalid frame format: {e}")

            tensor = detect_single_face(image)
            if tensor is None:
                continue
            face_tensors.append(tensor.face_crop_tensor)

        if len(face_tensors) < MIN_FRAMES_REQUIRED:
            raise ValidationError("Not enough recognizable faces found.")

        try:
            final_embedding = generate_average_embedding(face_tensors)
        except Exception as e:
            raise ValidationError("Failed to build facial profile")

        emb_list = final_embedding.vector.tolist()
        
        success = self.student_repo.update_embedding(self.institution_id, student_id, emb_list)
        if not success:
            raise ValidationError("Student not found or database constraint failure")

        # Reload cache to accept new student
        from backend.ml.matcher.optimized_recognition import get_embedding_cache
        from backend.core.config import REDIS_URL
        import redis
        
        cache = get_embedding_cache()
        cache.refresh(self.institution_id)

        try:
            r = redis.Redis.from_url(REDIS_URL)
            r.publish("cache:invalidation", self.institution_id)
        except Exception as e:
            print(f"Failed to publish invalidation: {e}")

        return True
