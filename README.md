# EduSolve 🎓

> **AI-Powered Learning & Doubt-Solving Platform for Class 9 & 10 Students**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Groq API](https://img.shields.io/badge/Inference-Groq%20Cloud-f55036.svg)](https://console.groq.com)
[![Model](https://img.shields.io/badge/LLM-Meta%20LLaMA--3.1--8B-purple.svg)](https://huggingface.co/meta-llama)
[![Tests](https://img.shields.io/badge/tests-84%20passed-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Architecture & Reusable Services](#-architecture--reusable-services)
- [Key Features](#-key-features)
- [Input Validation & Domain Guardrails](#-input-validation--domain-guardrails)
- [Structured Answers & Response Formats](#-structured-answers--response-formats)
- [Setup & Installation Guide](#-setup--installation-guide)
- [Usage Guide](#-usage-guide)
  - [1. Web Application Service (Django / FastAPI)](#1-web-application-service-django--fastapi)
  - [2. Interactive CLI Mode](#2-interactive-cli-mode)
  - [3. Legacy Script Interface (`ai_engine.py`)](#3-legacy-script-interface-ai_enginepy)
- [Running Automated Tests](#-running-automated-tests)
- [Error Handling & HTTP Status Mapping](#-error-handling--http-status-mapping)
- [Environment Variables](#-environment-variables)
- [Project Structure](#-project-structure)
- [Team](#-team)
- [License](#-license)

---

## 🌟 Overview

**EduSolve** is an AI academic tutor designed specifically for Indian curriculum (CBSE / State Boards) **Class 9 and 10 students**. Refactored from a standalone script into a resilient, production-ready service layer, EduSolve provides dependable core logic that powers web applications, background workers, and interactive learning tools.

Instead of monolithic scripts or unstructured text, EduSolve delivers:
1. **Strict Input Validation**: Pre-flight validation on classes (9 & 10), subjects (Science & Maths), and question sanity.
2. **Pedagogical 3-Part Answers**: Clear explanations tailored for 14–16 year olds, key formulas/facts, and relatable real-life analogies.
3. **Structured Pydantic Models**: Strongly-typed data schemas serializable directly to JSON for REST APIs.
4. **Resilient Error Handling**: Graceful translation of Groq API rate limits, timeouts, authentication errors, and JSON anomalies into typed exceptions with HTTP status codes.
5. **Comprehensive Test Suite**: Automated unit and integration tests covering validation, parsing, error recovery, and service orchestration.

---

## 🏗️ Architecture & Reusable Services

The core engine is structured into modular, single-responsibility services under `services/`:

```
services/
├── __init__.py         # Clean public package exports
├── config.py           # Configuration, constants, and subject aliases
├── exceptions.py       # Custom exception hierarchy with HTTP status codes
├── models.py           # Pydantic schemas (StructuredAnswer, PracticeQuestion, TutorResponse)
├── validators.py       # Grade, subject, and question input validators
├── prompts.py          # Centralized persona templates and prompt builders
├── parser.py           # Regex-based answer parser & fault-tolerant JSON question parser
├── groq_client.py      # Resilient Groq SDK wrapper with exception mapping
└── tutor_service.py    # High-level orchestrator service (TutorService)
```

---

## ⚡ Key Features

- 🎯 **Academic Guardrails**: Dedicated exclusively to **Science** and **Mathematics**. Off-topic questions are respectfully filtered out.
- 📐 **Structured 3-Part Pedagogical Schema**:
  - `explanation`: Age-appropriate conceptual walkthrough.
  - `key_formula_fact`: Core principles, equations, and definitions.
  - `real_example`: Real-world connection or everyday analogy.
- 🔄 **Automated Practice Generation**: Generates 3 contextual practice questions (MCQ + Short Answer) with complete solutions.
- 🛡️ **Graceful Groq Error Recovery**: Distinguishes rate limits, authentication errors, network timeouts, and JSON formatting quirks with custom domain exceptions.
- 🔌 **Ready for Any Web Framework**: Designed for seamless plug-in into Django REST Framework, FastAPI, or Flask.

---

## 🛡️ Input Validation & Domain Guardrails

All incoming inputs are rigorously validated before sending requests to the LLM:

| Field | Rule | Accepted Variations | Behavior on Failure |
|---|---|---|---|
| `grade` | Must be 9 or 10 | `9`, `10`, `"9"`, `"10"`, `"Class 9"`, `"9th"`, `"Grade 10"` | Raises `ValidationError` (400 Bad Request) |
| `subject` | Science or Maths | `"Science"`, `"Maths"`, `"math"`, `"mathematics"`, `"physics"`, `"chemistry"`, `"biology"`, `"algebra"` | Raises `ValidationError` (400 Bad Request) |
| `question` | 3 to 1500 chars | Non-empty string with alphanumeric characters | Raises `ValidationError` (400 Bad Request) |

---

## 📦 Structured Answers & Response Formats

The `TutorService` returns a strongly typed `TutorResponse` Pydantic model:

```json
{
  "success": true,
  "question": "Why does an object float or sink in water?",
  "subject": "Science",
  "grade": 9,
  "structured_answer": {
    "explanation": "Whether an object floats or sinks depends on its density compared to water...",
    "key_formula_fact": "Density = Mass / Volume (ρ = m / V). If Density < 1 g/cm³, it floats.",
    "real_example": "An iron nail sinks, but a massive hollow ship floats because of air volume.",
    "is_domain_match": true
  },
  "raw_answer": "EXPLANATION:\n...",
  "practice_questions": [
    {
      "question": "What is Archimedes' Principle?",
      "answer": "The buoyant upthrust equals the weight of displaced fluid.",
      "type": "short",
      "options": null
    }
  ],
  "model_used": "llama-3.1-8b-instant",
  "error": null
}
```

---

## 🚀 Setup & Installation Guide

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/aryan-65548/Edusolve.git
cd Edusolve

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Key

Copy `.env.example` to `.env` and insert your [Groq Cloud API Key](https://console.groq.com/keys):

```bash
cp .env.example .env
```

```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

---

## 💻 Usage Guide

### 1. Web Application Service (Django / FastAPI)

Import `TutorService` anywhere in your application:

```python
from services import TutorService, ValidationError, EduSolveError

tutor = TutorService()

try:
    response = tutor.solve_doubt(
        question="What is Pythagoras theorem?",
        subject="Maths",
        grade=10
    )
    # Convert directly to REST API JSON response:
    return response.to_api_response()

except ValidationError as exc:
    # 400 Bad Request with field details
    return {"error": exc.message, "field": exc.field}, 400

except EduSolveError as exc:
    # Maps directly to appropriate HTTP status (401, 429, 502, 503)
    return {"error": exc.message}, exc.status_code
```

Alternatively, use the safe, non-raising variant:

```python
# Returns TutorResponse with success=False and error message on failures
response = tutor.solve_doubt_safe(question="...", subject="Science", grade=9)
if not response.success:
    print("Error:", response.error)
```

### 2. Interactive CLI Mode

Run the interactive terminal tutor:

```bash
python ai_engine.py
```

The CLI features interactive prompts, input validation loops, and friendly error recovery.

### 3. Legacy Script Interface (`ai_engine.py`)

For backward compatibility with existing code:

```python
from ai_engine import ask_doubt, get_practice_questions, solve_doubt

# 1. Ask doubt (returns formatted string)
answer = ask_doubt("State Newton's second law", "Science", 9)

# 2. Get practice questions (returns list of dicts)
questions = get_practice_questions(answer, "Science", 9)

# 3. Solve doubt (returns complete dict)
result = solve_doubt("State Newton's second law", "Science", 9)
```

---

## 🧪 Running Automated Tests

EduSolve includes a comprehensive suite of unit and integration tests:

```bash
# Run tests with pytest
pytest -v

# Or run tests using python module
python -m pytest
```

### Test Coverage Highlights:
- **`tests/test_validators.py`**: Valid/invalid grades, aliases (e.g. `algebra` -> `Maths`), length boundaries, empty inputs.
- **`tests/test_parser.py`**: 3-part answers, markdown headers, domain rejections, malformed JSON recovery, trailing comma fixes.
- **`tests/test_groq_client.py`**: Authentication errors, rate limit handling, connection timeouts, generic API errors.
- **`tests/test_tutor_service.py`**: End-to-end orchestration, out-of-domain guardrail skipping, safe variants.
- **`tests/test_ai_engine_compatibility.py`**: Full backward compatibility verification for `ai_engine.py`.

---

## 🛡️ Error Handling & HTTP Status Mapping

EduSolve maps internal and upstream AI errors to standard HTTP status codes:

| Exception | HTTP Status | Trigger Condition |
|---|---|---|
| `ValidationError` | **400 Bad Request** | Invalid class (not 9 or 10), unsupported subject, empty/short question |
| `AuthenticationError` | **401 Unauthorized** | Missing or invalid `GROQ_API_KEY` |
| `RateLimitError` | **429 Too Many Requests** | Groq API quota or rate limit exceeded |
| `ServiceUnavailableError`| **503 Service Unavailable** | Groq API network connection failure or 5xx server downtime |
| `AIProviderError` | **502 Bad Gateway** | Unexpected upstream AI provider response |
| `ParsingError` | **502 Bad Gateway** | Unrecoverable AI completion formatting failure |

---

## 🔑 Environment Variables

| Variable | Description | Required | Default |
|---|---|---|---|
| `GROQ_API_KEY` | Groq Cloud API Key | **Yes** | `""` |

---

## 👥 Team

EduSolve is built with ❤️ by:

- **Aryan Patel**
- **Rudra Bhungaliya**
- **Vishvarajsinh Zala**
- **Team Collaborators**

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
