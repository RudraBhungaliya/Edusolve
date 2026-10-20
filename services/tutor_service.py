"""
Core EduSolve AI Tutor Service.
Orchestrates validation, prompt creation, Groq LLM inference, structured parsing,
and practice question generation.
"""

from typing import Any, List, Optional

from services.config import DEFAULT_MODEL
from services.exceptions import EduSolveError
from services.groq_client import GroqService
from services.models import PracticeQuestion, StructuredAnswer, TutorResponse
from services.parser import parse_practice_questions, parse_structured_answer
from services.prompts import (
    PRACTICE_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    build_doubt_prompt,
    build_practice_prompt,
)
from services.validators import validate_doubt_input, validate_grade, validate_subject


class TutorService:
    """
    High-level, reusable AI tutor service designed for web applications and CLI clients.
    """

    def __init__(
        self,
        groq_service: Optional[GroqService] = None,
        model: str = DEFAULT_MODEL,
    ):
        self.groq_service = groq_service or GroqService(default_model=model)
        self.model = model

    def ask_doubt_raw(self, question: Any, subject: Any, grade: Any) -> str:
        """
        Validate inputs and query Groq for the raw 3-part pedagogical response string.
        """
        clean_q, clean_subj, clean_grade = validate_doubt_input(question, subject, grade)
        prompt = build_doubt_prompt(clean_q, clean_subj, clean_grade)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        return self.groq_service.generate_chat_completion(
            messages=messages,
            model=self.model,
            temperature=0.2,
        )

    def ask_doubt(self, question: Any, subject: Any, grade: Any) -> StructuredAnswer:
        """
        Validate input, query AI tutor, and return parsed StructuredAnswer.
        """
        raw_text = self.ask_doubt_raw(question, subject, grade)
        return parse_structured_answer(raw_text)

    def generate_practice_questions(
        self, ai_answer: str, subject: Any, grade: Any
    ) -> List[PracticeQuestion]:
        """
        Generate 3 practice questions (MCQ + Short Answer) based on the AI's explanation.
        Returns an empty list if the explanation is empty or rejected by guardrails.
        """
        if not ai_answer or not ai_answer.strip():
            return []

        clean_subj = validate_subject(subject)
        clean_grade = validate_grade(grade)

        prompt = build_practice_prompt(ai_answer, clean_subj, clean_grade)
        messages = [
            {"role": "system", "content": PRACTICE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        try:
            raw_json = self.groq_service.generate_chat_completion(
                messages=messages,
                model=self.model,
                temperature=0.3,
            )
            return parse_practice_questions(raw_json)
        except EduSolveError:
            # For practice questions, fail gracefully so the core explanation is still delivered
            return []

    def solve_doubt(self, question: Any, subject: Any, grade: Any) -> TutorResponse:
        """
        End-to-end tutor orchestration:
          1. Validates inputs (grade: 9/10, subject: Science/Maths, question length).
          2. Generates pedagogical answer from Groq LLM.
          3. Parses into structured breakdown (Explanation, Formula/Fact, Real Example).
          4. Generates contextual practice questions if within curriculum domain.
          5. Assembles and returns typed TutorResponse.
        """
        clean_q, clean_subj, clean_grade = validate_doubt_input(question, subject, grade)

        # 1. Fetch AI doubt answer
        raw_answer = self.ask_doubt_raw(clean_q, clean_subj, clean_grade)
        structured_ans = parse_structured_answer(raw_answer)

        # 2. Generate practice questions only if within curriculum scope
        practice_questions: List[PracticeQuestion] = []
        if structured_ans.is_domain_match:
            practice_questions = self.generate_practice_questions(
                ai_answer=raw_answer,
                subject=clean_subj,
                grade=clean_grade,
            )

        return TutorResponse(
            success=True,
            question=clean_q,
            subject=clean_subj,
            grade=clean_grade,
            structured_answer=structured_ans,
            raw_answer=raw_answer,
            practice_questions=practice_questions,
            model_used=self.model,
        )

    def solve_doubt_safe(self, question: Any, subject: Any, grade: Any) -> TutorResponse:
        """
        Non-raising variant suitable for APIs that prefer returning status objects
        rather than handling uncaught exceptions.
        """
        try:
            return self.solve_doubt(question, subject, grade)
        except EduSolveError as exc:
            placeholder_answer = StructuredAnswer(
                explanation=exc.message,
                key_formula_fact="N/A",
                real_example="N/A",
                is_domain_match=False,
            )
            return TutorResponse(
                success=False,
                question=str(question or ""),
                subject=str(subject or "Science"),
                grade=int(grade) if isinstance(grade, int) and grade in (9, 10) else 9,
                structured_answer=placeholder_answer,
                raw_answer=exc.message,
                practice_questions=[],
                model_used=self.model,
                error=exc.message,
            )
