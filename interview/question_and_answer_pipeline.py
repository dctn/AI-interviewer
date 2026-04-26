from django.conf import settings
from django.shortcuts import get_object_or_404
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_groq import ChatGroq
from core.LLM_prompt import PROMPT_jd, PROMPT_question_generation, PROMPT_ANSWER_EVAL_BATCH
from interview.models import *

def question_generation(resume,jd,experience_level,difficulty):
    resume = PyPDFLoader(file_path=resume)
    json_parser = JsonOutputParser()
    gpt_20b = ChatGroq(api_key=settings.GROQ_API_KEY,model='openai/gpt-oss-20b')
    gpt_120b = ChatGroq(api_key=settings.GROQ_API_KEY,model='openai/gpt-oss-120b')
    resume_data = [doc.page_content for doc in resume.load()]
    resume_text = "".join(resume_data)


    jd_chain = PROMPT_jd | gpt_20b | StrOutputParser()
    question_chain = PROMPT_question_generation | gpt_120b | json_parser

    jd_data = jd_chain.invoke({
        "detail":jd,
        'resume':resume_text
    })

    question_response = question_chain.invoke({
        'resume':resume_text,
        'jd':jd_data,
        'experience_level':experience_level,
        'difficulty':difficulty
    })

    # print(question_response)
    return question_response


def answer_evaluation(interview_id):
    gpt_120b = ChatGroq(api_key=settings.GROQ_API_KEY,model='openai/gpt-oss-120b')
    json_parser = JsonOutputParser()

    interview = Interview.objects.get(interview_id=interview_id)
    interview.status = 'processing'
    interview.save()

    questions = QuestionAndAnswer.objects.filter(interview_id=interview_id)

    eval_chain = PROMPT_ANSWER_EVAL_BATCH | gpt_120b | json_parser

    question_batch = []
    answer_batch = []
    EVAL_BATCH_SIZE = 3
    for i,question in enumerate(questions):
        if question.answer_audio_transcript is not None:
            if len(question_batch) <= EVAL_BATCH_SIZE:
                question_batch.append({'question':question.question,
                                    "user_answer":question.answer_audio_transcript,
                                    'question_id':question.question_id})

            if EVAL_BATCH_SIZE == len(question_batch):
                answer_batch.extend(eval_chain.invoke({
                    'qa_list':question_batch,
                }))
                question_batch = []

    if question_batch:
        answer_batch.extend(eval_chain.invoke({
            'qa_list':question_batch,
        }))

    print(answer_batch)
    # storing result of question and answer
    for answer in answer_batch:
        question = get_object_or_404(QuestionAndAnswer, question_id=answer['question_id'])
        question.analysis_json = answer['analysis_report']
        question.expected_answer = answer['analysis_report']['expected_answer']
        question.score = answer['analysis_report']['overall_score']
        question.save()

    interview.status = 'completed'
    interview.save()
    return None