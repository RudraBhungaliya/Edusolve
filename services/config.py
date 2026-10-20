"""
Configuration settings for the EduSolve AI Tutor services.
"""

import os
from typing import Dict, List, Set
from dotenv import load_dotenv

# Load .env file automatically
load_dotenv()

# Groq API configuration
GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")

# Default LLM model
DEFAULT_MODEL: str = "llama-3.1-8b-instant"

# Supported alternative models
ALTERNATIVE_MODELS: List[str] = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
]

# Educational constraints
SUPPORTED_GRADES: Set[int] = {9, 10}

# Standardized subjects
SUBJECT_SCIENCE: str = "Science"
SUBJECT_MATHS: str = "Maths"
SUPPORTED_SUBJECTS: Set[str] = {SUBJECT_SCIENCE, SUBJECT_MATHS}

# Subject alias normalization mapping
SUBJECT_ALIASES: Dict[str, str] = {
    # Mathematics aliases
    "math": SUBJECT_MATHS,
    "maths": SUBJECT_MATHS,
    "mathematics": SUBJECT_MATHS,
    "algebra": SUBJECT_MATHS,
    "geometry": SUBJECT_MATHS,
    "trigonometry": SUBJECT_MATHS,
    "arithmetic": SUBJECT_MATHS,
    # Science aliases
    "science": SUBJECT_SCIENCE,
    "sci": SUBJECT_SCIENCE,
    "physics": SUBJECT_SCIENCE,
    "chemistry": SUBJECT_SCIENCE,
    "biology": SUBJECT_SCIENCE,
}

# Request configuration
DEFAULT_TIMEOUT_SECONDS: float = 30.0
MAX_QUESTION_LENGTH: int = 1500
MIN_QUESTION_LENGTH: int = 3
