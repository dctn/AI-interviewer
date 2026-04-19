from typing import List
from .question_schemas import QuestionItem


def normalize_question_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


def deduplicate_questions(questions: List[QuestionItem]) -> List[QuestionItem]:
    seen = set()
    unique_questions = []

    for item in questions:
        normalized = normalize_question_text(item.question)
        if normalized not in seen:
            seen.add(normalized)
            unique_questions.append(item)

    for idx, item in enumerate(unique_questions, start=1):
        item.question_no = idx

    return unique_questions

