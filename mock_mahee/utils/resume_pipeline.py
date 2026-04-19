from .pdf_parser import extract_text_from_pdf
from .resume_cleaner import clean_resume_text
from .resume_prompt import build_resume_analysis_prompt
from .groq_resume_client import analyze_resume_with_groq, fix_resume_json_with_groq
from .resume_validator import parse_and_validate_resume_output
from .resume_schemas import ResumeAnalysisResponse


def run_resume_analysis_pipeline(file_path):
    raw_text = extract_text_from_pdf(file_path)

    # Clean text WITH emails preserved for LLM analysis (so it can extract contact info)
    text_for_llm = clean_resume_text(raw_text, remove_emails=False, remove_urls=False)
    # Clean text for downstream usage (question generation etc.)
    cleaned_text = clean_resume_text(raw_text)

    prompt = build_resume_analysis_prompt(text_for_llm)
    raw_output = analyze_resume_with_groq(prompt)

    try:
        validated_output = parse_and_validate_resume_output(raw_output, cleaned_text)
    except:
        fixed_output = fix_resume_json_with_groq(raw_output)
        validated_output = parse_and_validate_resume_output(fixed_output, cleaned_text)

    return validated_output
