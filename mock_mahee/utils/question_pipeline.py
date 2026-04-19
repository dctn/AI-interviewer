from typing import List, Tuple
from pydantic import BaseModel, Field
from typing import Literal, Optional
from .question_schemas import QuestionGenerationRequest, QuestionGenerationResponse
from .question_cleaner import clean_text
from .chunker import chunk_text
from .retriever import retrieve_top_k_chunks_with_scores
from .question_prompt import build_question_prompt
from .groq_questions_client import generate_questions_from_groq, fix_json_with_groq
from .question_validator import parse_and_validate_question_output
from .question_deduplicator import deduplicate_questions


def run_question_generation_pipeline(
    request: QuestionGenerationRequest
) -> QuestionGenerationResponse:
    cleaned_resume = clean_text(request.resume_text)
    cleaned_jd = clean_text(request.job_description)

    resume_chunks = chunk_text(cleaned_resume, max_chunk_length=400)

    retrieval_query = f"Role: {request.role}\nJob Description: {cleaned_jd}"

    top_chunks_with_scores = retrieve_top_k_chunks_with_scores(
        query_text=retrieval_query,
        chunks=resume_chunks,
        top_k=3
    )

    print("\n===== TOP RETRIEVED CHUNKS =====")
    for i, (chunk, score) in enumerate(top_chunks_with_scores, start=1):
        print(f"\nChunk {i} | Score: {score:.4f}\n{chunk}")

    prompt = build_question_prompt(
        role=request.role,
        job_description=cleaned_jd,
        retrieved_resume_chunks=top_chunks_with_scores,
        question_count=request.question_count,
        difficulty=request.difficulty
    )

    raw_output = generate_questions_from_groq(prompt)

    try:
        validated_output = parse_and_validate_question_output(raw_output)
    except Exception:
        fixed_output = fix_json_with_groq(raw_output)
        validated_output = parse_and_validate_question_output(fixed_output)

    unique_questions = deduplicate_questions(validated_output.questions)

    final_questions = unique_questions[:request.question_count]

    for idx, item in enumerate(final_questions, start=1):
        item.question_no = idx

    return QuestionGenerationResponse(questions=final_questions)
