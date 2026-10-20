"""
Author: Aryan Patel, Rudra Bhungaliya, Vishvarajsinh Zala
Date of creation: 20th Feb 2026
Refactored: April 2026 (Service-Oriented Core Architecture for EduSolve)

This module provides the core interface for the EduSolve AI Tutor.
It delegates to reusable backend services and offers backward-compatible
helper functions for CLI and web integrations.

Work well dont hallucinate.
"""

import sys
from typing import Any, Dict, List

from services import (
    AuthenticationError,
    EduSolveError,
    RateLimitError,
    ServiceUnavailableError,
    TutorService,
    ValidationError,
    validate_grade,
    validate_question,
    validate_subject,
)

# Shared default service instance
_tutor_service = TutorService()


def ask_doubt(question: str, subject: str, grade: int) -> str:
    """
    Submit an academic doubt and receive the raw pedagogical explanation string.

    Parameters:
      question (str): The academic question/doubt.
      subject (str): 'Science' or 'Maths'.
      grade (int): 9 or 10.

    Returns:
      str: Formatted 3-part explanation (EXPLANATION, KEY FORMULA / FACT, REAL EXAMPLE).
    """
    return _tutor_service.ask_doubt_raw(question=question, subject=subject, grade=grade)


def get_practice_questions(ai_answer: str, subject: str, grade: int) -> List[Dict[str, Any]]:
    """
    Generate 3 practice questions with answers based on the AI tutor's explanation.

    Parameters:
      ai_answer (str): The explanation text provided by the AI tutor.
      subject (str): 'Science' or 'Maths'.
      grade (int): 9 or 10.

    Returns:
      list: List of question dictionaries with keys 'question', 'answer', 'type'.
    """
    questions = _tutor_service.generate_practice_questions(
        ai_answer=ai_answer, subject=subject, grade=grade
    )
    return [q.to_dict() for q in questions]


def solve_doubt(question: str, subject: str, grade: int) -> Dict[str, Any]:
    """
    End-to-end doubt resolution returning both structured answer and practice questions.

    Returns dictionary matching legacy contract:
    {
      "question": str,
      "subject": str,
      "grade": int,
      "answer": str,
      "practice_questions": list[dict],
      "structured_answer": dict
    }
    """
    print(f"\n Thinking about: {question}\n")
    response = _tutor_service.solve_doubt(question=question, subject=subject, grade=grade)
    return response.to_legacy_dict()


# ---------------------------------------------------------------------------
# CLI Interactive Prompts & Terminal Runner
# ---------------------------------------------------------------------------

def get_grade() -> int:
    """Prompt user for a valid grade (9 or 10) with validation."""
    while True:
        grade_input = input("Enter your Class (9 or 10): ").strip()
        try:
            return validate_grade(grade_input)
        except ValidationError as err:
            print(f"❌ {err.message}")


def get_subject() -> str:
    """Prompt user for a valid subject (Science or Maths)."""
    while True:
        print("\nChoose Subject:")
        print("  1. Science")
        print("  2. Maths")
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            return "Science"
        if choice == "2":
            return "Maths"

        # Also support typing the subject name directly
        try:
            return validate_subject(choice)
        except ValidationError:
            print("❌ Invalid choice. Please enter 1, 2, 'Science', or 'Maths'.")


def get_question() -> str:
    """Prompt user for a valid, non-empty academic question."""
    while True:
        question = input("\nType your doubt/question: ").strip()
        try:
            return validate_question(question)
        except ValidationError as err:
            print(f"❌ {err.message}")


def run_cli() -> None:
    """Main terminal loop with user-friendly error recovery."""
    print("=" * 60)
    print("         Welcome to EduSolve AI Tutor 🎓")
    print("     For Class 9 & 10 | Science & Maths")
    print("=" * 60)

    while True:
        try:
            # Collect validated inputs
            grade = get_grade()
            subject = get_subject()
            question = get_question()

            # Execute AI doubt resolution
            result = solve_doubt(question=question, subject=subject, grade=grade)

            # Display answer
            print("\n" + "=" * 60)
            print("ANSWER:")
            print("=" * 60)
            print(result["answer"])

            # Display practice questions
            if result["practice_questions"]:
                print("\n" + "=" * 60)
                print("PRACTICE QUESTIONS:")
                print("=" * 60)
                for i, q in enumerate(result["practice_questions"], 1):
                    q_type = q.get("type", "short").upper()
                    print(f"\nQ{i} [{q_type}]: {q['question']}")
                    print(f"   Answer: {q['answer']}")

        except AuthenticationError as exc:
            print(f"\n🔒 Authentication Error: {exc.message}")
            print("👉 Please ensure GROQ_API_KEY is set in your .env file or environment.")
            break
        except RateLimitError as exc:
            print(f"\n⏳ Rate Limit Reached: {exc.message}")
        except ServiceUnavailableError as exc:
            print(f"\n⚠️ Service Notice: {exc.message}")
        except EduSolveError as exc:
            print(f"\n❌ Error: {exc.message}")
        except KeyboardInterrupt:
            print("\n\nSession interrupted by user.")
            break

        # Ask if user wants to continue
        print("\n" + "-" * 60)
        again = input("Ask another doubt? (yes/no): ").strip().lower()
        if again not in ["yes", "y"]:
            print("\nGoodbye! Keep studying! 🚀")
            break
        print()


if __name__ == "__main__":
    run_cli()