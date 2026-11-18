from app.models.course import (
    Course,
    CourseSlug,
    Module,
    Practical,
    PracticalFormat,
    QuizQuestion,
)
from app.models.progress import QuizAttempt, Submission
from app.models.user import AcademicGroup, User, UserRole

__all__ = [
    "AcademicGroup",
    "Course",
    "CourseSlug",
    "Module",
    "Practical",
    "PracticalFormat",
    "QuizAttempt",
    "QuizQuestion",
    "Submission",
    "User",
    "UserRole",
]
