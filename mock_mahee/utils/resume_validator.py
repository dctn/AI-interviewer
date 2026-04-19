import json
from typing import Dict, Any
from .resume_schemas import ResumeAnalysisResponse


def parse_and_validate_resume_output(raw_output: str, cleaned_text: str) -> Dict[str, Any]:
    try:
        # Try to parse JSON
        data = json.loads(raw_output)

        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'summary']
        for field in required_fields:
            if field not in data:
                data[field] = "Not found"

        # Ensure lists are lists
        list_fields = ['skills', 'projects', 'education', 'experience', 'certifications']
        for field in list_fields:
            if field not in data:
                data[field] = []
            elif not isinstance(data[field], list):
                data[field] = [str(data[field])]

        data['raw_text'] = cleaned_text

        # Validate with Pydantic schema
        ResumeAnalysisResponse(**data)

        return data

    except json.JSONDecodeError:
        raise ValueError("Invalid JSON from LLM")
    except Exception as e:
        raise ValueError(f"Validation failed: {str(e)}")
