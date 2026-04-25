from django.conf import settings
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_groq import ChatGroq
from core.LLM_prompt import PROMPT_jd, PROMPT_question_generation

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

    print(question_response)
    return question_response