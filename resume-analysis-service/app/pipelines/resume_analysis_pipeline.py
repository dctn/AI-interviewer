from app.preprocess.pdf_parser import extract_text_from_pdf
from app.preprocess.cleaner import clean_text
from app.prompts.resume_analysis_prompt import build_resume_analysis_prompt
from app.integrations.groq_client import analyze_resume_with_groq, fix_resume_json_with_groq
from app.postprocess.validator import parse_and_validate_resume_output
from app.schemas.resume_analysis import ResumeAnalysisResponse


def run_resume_analysis_pipeline(file_path: str) -> ResumeAnalysisResponse:
    raw_text = extract_text_from_pdf(file_path)
    cleaned_text = clean_text(raw_text)

    prompt = build_resume_analysis_prompt(cleaned_text)

    raw_output = analyze_resume_with_groq(prompt)

    try:
        validated_output = parse_and_validate_resume_output(raw_output, cleaned_text)
    except Exception:
        fixed_output = fix_resume_json_with_groq(raw_output)
        validated_output = parse_and_validate_resume_output(fixed_output, cleaned_text)

    return validated_output