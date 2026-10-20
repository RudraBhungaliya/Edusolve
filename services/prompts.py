"""
Centralized prompt templates and persona definitions for EduSolve AI Tutor.
"""

# Canonical system prompt defining persona, constraints, and 3-part pedagogical response format
SYSTEM_PROMPT = """
You are EduSolve AI, a tutor for Indian Class 9 and 10 students.
You ONLY answer Science and Mathematics questions.
If the question is not about Science or Maths, reply:
"I only help with Science and Maths doubts!"

Always respond in this exact format:

EXPLANATION:
(explain clearly in simple language for a 15 year old)

KEY FORMULA / FACT:
(the most important formula or fact)

REAL EXAMPLE:
(one simple real life example)
""".strip()

OUT_OF_DOMAIN_REPLY = "I only help with Science and Maths doubts!"

PRACTICE_SYSTEM_PROMPT = "Return only valid JSON. No explanation, no markdown."


def build_doubt_prompt(question: str, subject: str, grade: int) -> str:
    """Format the student doubt into the structured user prompt."""
    return f"[Class {grade}] [{subject}] Student doubt: {question}"


def build_practice_prompt(ai_answer: str, subject: str, grade: int) -> str:
    """Format the prompt for generating 3 practice questions with solutions."""
    return f"""
Based on this explanation given to a Class {grade} {subject} student:
{ai_answer}

Generate exactly 3 practice questions.
Return ONLY a JSON array like this, nothing else:
[
  {{"question": "...", "answer": "...", "type": "mcq"}},
  {{"question": "...", "answer": "...", "type": "short"}},
  {{"question": "...", "answer": "...", "type": "short"}}
]
""".strip()
