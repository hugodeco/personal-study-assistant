"""Validate quiz JSON files in the project's `forms/` directory.

Usage:
    python validate.py <form_name>

Examples:
    python validate.py energia_renovavel_nao_renovavel
    python validate.py other_quiz.json

What this script does:
    - Loads a JSON file from the `forms/` folder (accepts name with or without .json).
    - Checks required top-level keys: metadata, content, questions.
    - Validates metadata fields: title, description, subject, grade, topic.
    - Validates each question: unique integer id, section, question text, options (2-6 unique strings), correct_answer index in range.
    - Checks optional difficulty values against allowed set ("fácil", "médio", "difícil").
    - Prints validation errors and exits with a non-zero code on failure.

Exit codes:
    0 - validation passed
    2 - validation failed or file not found / invalid JSON

Notes:
    - The script is intended to be run before publishing a form to ensure the JSON meets the project's schema constraints.
    - Keep this file in the project root so `form.py` can call it before publishing.
"""
import sys
from pathlib import Path

# Reuse validation logic from previous script (embedded for simplicity)

def validate_quiz(path: Path) -> int:
    required_metadata = ["title", "description", "subject", "grade", "topic"]
    allowed_difficulties = {"fácil", "médio", "difícil"}

    errors = []

    if not path.exists():
        print(f"ERROR: quiz file not found: {path}")
        return 2

    try:
        import json
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        print("ERROR: invalid JSON:", e)
        return 2

    for key in ("metadata", "content", "questions"):
        if key not in data:
            errors.append(f"Missing top-level key: {key}")

    meta = data.get("metadata", {})
    for k in required_metadata:
        if k not in meta or (isinstance(meta.get(k), str) and not meta.get(k).strip()):
            errors.append(f"Missing or empty metadata field: {k}")

    questions = data.get("questions")
    if not isinstance(questions, list) or len(questions) == 0:
        errors.append("'questions' must be a non-empty array")
    else:
        ids = set()
        for i, q in enumerate(questions, start=1):
            prefix = f"question[{i}]"
            qid = q.get("id")
            if not isinstance(qid, int):
                errors.append(f"{prefix}: 'id' missing or not integer")
            else:
                if qid in ids:
                    errors.append(f"Duplicate id: {qid}")
                ids.add(qid)
            for rk in ("section", "question", "options", "correct_answer"):
                if rk not in q:
                    errors.append(f"{prefix}: missing field '{rk}'")
            opts = q.get("options")
            if not isinstance(opts, list):
                errors.append(f"{prefix}: 'options' must be an array")
            else:
                if not (2 <= len(opts) <= 6):
                    errors.append(f"{prefix}: 'options' length must be between 2 and 6 (got {len(opts)})")
                cleaned = [str(x).strip() for x in opts]
                if len(set(cleaned)) != len(cleaned):
                    errors.append(f"{prefix}: duplicate option texts found")
            ca = q.get("correct_answer")
            if not isinstance(ca, int):
                errors.append(f"{prefix}: 'correct_answer' must be integer index")
            else:
                if isinstance(opts, list):
                    if not (0 <= ca < len(opts)):
                        errors.append(f"{prefix}: 'correct_answer' index {ca} out of range for options length {len(opts)}")
            diff = q.get("difficulty")
            if diff is not None and diff not in allowed_difficulties:
                errors.append(f"{prefix}: invalid difficulty '{diff}'")

    if errors:
        print("VALIDATION FAILED. Issues found:")
        for e in errors:
            print(" -", e)
        return 2

    print("VALIDATION PASSED: quiz looks good (basic checks).")
    return 0


def main(argv):
    if len(argv) < 2:
        print("Usage: python validate.py <form_name>")
        return 2
    form_name = argv[1]
    if form_name.endswith('.json'):
        filename = form_name
    else:
        filename = form_name + '.json'
    root = Path(__file__).resolve().parent
    forms_dir = root / 'forms'
    quiz_path = forms_dir / filename
    return validate_quiz(quiz_path)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
