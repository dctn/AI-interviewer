from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from langchain_groq import ChatGroq
from groq import Groq
from django.conf import settings
from interview.question_generation import question_generation
from interview.forms import InterviewForm
from interview.models import *
import json

# Create your views here.

def interview_setup(request):
    if request.method == 'POST':
        form = InterviewForm(request.POST,request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.user = request.user
            data.save()

            # question generation
            questions = question_generation(data.resume.path,data.jd,data.experience,data.difficulty)
            for i,question in enumerate(questions['questions']):
                QuestionAndAnswer.objects.create(
                    question=question['question'],
                    order_no=i,
                    question_domain= question['question_domain']+"/"+question['sub_domain'],
                    category=question['category'],
                    interview_id=data.interview_id,
                )

            return redirect('interview',data.interview_id)
    else:
        form = InterviewForm()

    return render(request, 'interview_setup.html', {'form':form})

def interview(request,interview_id):
    questions = QuestionAndAnswer.objects.filter(interview_id=interview_id).order_by('order_no').values('question_id','question')[:1]

    all_questions = {}
    for i,question in enumerate(questions):
        all_questions[i+1] = {'question':question['question'],"question_id":str(question['question_id'])}

    print(all_questions)
    context = {'questions':all_questions}
    return render(request, 'interview.html',context)

def result(request):
    if request.method == 'POST':
        groq = Groq(api_key=settings.GROQ_API_KEY)

        audio_file = request.FILES.getlist('audio_files')
        question_id = request.POST.getlist('question_ids')
        question_text = request.POST.getlist('question_text')

        transcriptions = []
        for i,audio_file in enumerate(audio_file):
            response = groq.audio.transcriptions.create(file=(audio_file.name,audio_file.read()),
                                                    model='whisper-large-v3-turbo')
            print(response.text)
            transcriptions.append(response.text)
        print(transcriptions)
        return JsonResponse({"test":'123'},content_type="application/json")