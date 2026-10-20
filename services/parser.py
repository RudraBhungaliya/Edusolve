"""
Robust response parsers for AI-generated answers and practice questions.
Handles markdown formatting, flexible regex header boundaries, and JSON quirks.
"""

import json
import re
from typing import List

from services.models import PracticeQuestion, StructuredAnswer
from services.prompts import OUT_OF_DOMAIN_REPLY


def is_out_of_domain(text: str) -> bool:
    """Check if the AI tutor rejected the question as out-of-domain."""
    normalized = text.strip().lower()
    return "i only help with science and maths" in normalized or "only answer science and mathematics" in normalized


def parse_structured_answer(raw_text: str) -> StructuredAnswer:
    """
    Parse the AI tutor's raw response into a StructuredAnswer object.

    Extracts:
      - EXPLANATION
      - KEY FORMULA / FACT
      - REAL EXAMPLE

    If headers are missing or formatted with markdown, graceful fallbacks ensure
    clean extraction without throwing uncaught exceptions.
    """
    if not raw_text or not raw_text.strip():
        return StructuredAnswer(
            explanation="No explanation was provided by the AI tutor.",
            key_formula_fact="N/A",
            real_example="N/A",
            is_domain_match=True,
        )

    clean_text = raw_text.strip()

    # Check for domain policy rejection
    if is_out_of_domain(clean_text):
        return StructuredAnswer(
            explanation=OUT_OF_DOMAIN_REPLY,
            key_formula_fact="N/A",
            real_example="N/A",
            is_domain_match=False,
        )

    # Patterns matching headers with optional markdown (**, ##, :) and casing
    exp_pattern = r"(?:^|\n)(?:#{1,3}\s*)?(?:\*\*)?EXPLANATION:?(?:\*\*)?:?\s*"
    key_pattern = r"(?:^|\n)(?:#{1,3}\s*)?(?:\*\*)?KEY\s+(?:FORMULA\s*(?:\/|AND)?\s*FACT|FORMULA|FACT):?(?:\*\*)?:?\s*"
    eg_pattern = r"(?:^|\n)(?:#{1,3}\s*)?(?:\*\*)?REAL(?:\s+LIFE)?\s+EXAMPLE:?(?:\*\*)?:?\s*"

    exp_match = re.search(exp_pattern, clean_text, re.IGNORECASE)
    key_match = re.search(key_pattern, clean_text, re.IGNORECASE)
    eg_match = re.search(eg_pattern, clean_text, re.IGNORECASE)

    # Standard case: All 3 sections found in order
    if exp_match and key_match and eg_match:
        exp_start = exp_match.end()
        key_start = key_match.start()
        explanation = clean_text[exp_start:key_start].strip()

        key_content_start = key_match.end()
        eg_start = eg_match.start()
        key_formula = clean_text[key_content_start:eg_start].strip()

        eg_content_start = eg_match.end()
        real_example = clean_text[eg_content_start:].strip()

        return StructuredAnswer(
            explanation=explanation or clean_text,
            key_formula_fact=key_formula or "N/A",
            real_example=real_example or "N/A",
            is_domain_match=True,
        )

    # Partial matches or unconventional formatting
    explanation = clean_text
    key_formula = "Key concepts and formulas are integrated into the explanation above."
    real_example = "Refer to the explanation above for contextual real-world examples."

    if exp_match and key_match:
        exp_start = exp_match.end()
        key_start = key_match.start()
        explanation = clean_text[exp_start:key_start].strip()
        key_formula = clean_text[key_match.end():].strip()
    elif key_match and eg_match:
        explanation = clean_text[:key_match.start()].strip()
        key_formula = clean_text[key_match.end():eg_match.start()].strip()
        real_example = clean_text[eg_match.end():].strip()
    elif exp_match:
        explanation = clean_text[exp_match.end():].strip()

    return StructuredAnswer(
        explanation=explanation or clean_text,
        key_formula_fact=key_formula,
        real_example=real_example,
        is_domain_match=True,
    )


def clean_json_string(raw: str) -> str:
    """Strip markdown code fence blocks and find JSON array boundaries."""
    text = raw.strip()
    # Strip ```json ... ``` or ``` ... ```
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    # Find the outermost array brackets [ ... ]
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
        # Remove trailing commas before closing braces/brackets (common LLM JSON issue)
        cleaned = re.sub(r",\s*([}\]])", r"\1", candidate)
        return cleaned

    return ""


def parse_practice_questions(raw_output: str) -> List[PracticeQuestion]:
    """
    Parse LLM response into a list of validated PracticeQuestion objects.
    Safely recovers from markdown wrappers, invalid characters, or partial JSON.
    """
    if not raw_output or not raw_output.strip():
        return []

    json_str = clean_json_string(raw_output)
    if not json_str:
        return []

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    parsed_questions: List[PracticeQuestion] = []
    for item in data:
        if isinstance(item, dict) and "question" in item and "answer" in item:
            q_text = str(item.get("question", "")).strip()
            ans_text = str(item.get("answer", "")).strip()
            q_type = str(item.get("type", "short")).strip().lower()
            if q_type not in ("mcq", "short"):
                q_type = "short"

            options = item.get("options")
            valid_options = None
            if isinstance(options, list) and all(isinstance(opt, str) for opt in options):
                valid_options = options

            if q_text and ans_text:
                parsed_questions.append(
                    PracticeQuestion(
                        question=q_text,
                        answer=ans_text,
                        type=q_type,  # type: ignore
                        options=valid_options,
                    )
                )

    return parsed_questions
