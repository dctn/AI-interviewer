import json
from .question_schemas import QuestionGenerationResponse, QuestionItem


def extract_json_from_text(raw_output: str) -> str:
    raw_output = raw_output.strip()
    start_index = raw_output.find("{")
    end_index = raw_output.rfind("}")

    if start_index == -1 or end_index == -1:
        raise ValueError("No valid JSON object found in model output")

    return raw_output[start_index:end_index + 1]


def parse_and_validate_question_output(raw_output: str) -> QuestionGenerationResponse:
    json_text = extract_json_from_text(raw_output)
    data = json.loads(json_text)

    # Validate with Pydantic schema
    response = QuestionGenerationResponse(**data)
    return response
