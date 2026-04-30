from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_groq import ChatGroq
from core.LLM_prompt import *
from django.conf import settings



def llm_resume_analysis(resume,jd_details):
    pdf_loader = PyPDFLoader(file_path=resume)
    json_parser = JsonOutputParser()
    str_parser = StrOutputParser()

    resume_data = [doc.page_content for doc in pdf_loader.load()]

    resume_text = "\n".join(resume_data).strip()
    resume_lower = resume_text.lower()

    try:
        gpt_120b = ChatGroq(api_key=settings.GROQ_API_KEY, model='openai/gpt-oss-120b',temperature=0)
        gpt_20b = ChatGroq(api_key=settings.GROQ_API_KEY, model='openai/gpt-oss-20b')
    except:
        gpt_120b = ChatOpenAI(api_key=settings.OPEN_ROUTER_KEY,model='openai/gpt-oss-120b',temperature=0,base_url="https://openrouter.ai/api/v1")
        gpt_20b = ChatOpenAI(api_key=settings.OPEN_ROUTER_KEY,model='openai/gpt-oss-20b',temperature=0,base_url="https://openrouter.ai/api/v1")


    jd_chain = PROMPT_jd | gpt_20b | str_parser
    keyword_chain = PROMPT_keyword | gpt_120b | json_parser

    jd = jd_chain.invoke({'detail':jd_details,'resume':resume_text})

    keyword = keyword_chain.invoke({'jd':jd})
    keywords = [key.lower().strip() for key in keyword]

    def is_match(kw, text):
        if kw in text:
            return True
        words = kw.split()
        if len(words) > 1:
            return all(w in text for w in words)
        return False

    matched_keyword = [kw for kw in keywords if is_match(kw, resume_lower)]
    mis_matched_keyword = [kw for kw in keywords if not is_match(kw, resume_lower)]
    kw_score = round((len(matched_keyword) / len(keywords)) * 100, 2) if keywords else 0


    chain = PROMPT_resume_analysis | gpt_120b | json_parser

    response = chain.invoke({
        "resume": resume_text,
        "jd": jd,
        "keyword": keyword,
        "kw_score": kw_score,
        "matched_count": len(matched_keyword),
        "total_keywords": len(keyword),
        "matched_keywords": matched_keyword,
        "missing_keywords": mis_matched_keyword,
    })



    return response,jd