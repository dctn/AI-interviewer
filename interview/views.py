from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from langchain_groq import ChatGroq
from groq import Groq
from django.conf import settings
from interview.question_and_answer_pipeline import question_generation, answer_evaluation
from interview.forms import InterviewForm
from interview.models import *
from django.utils import timezone
from core.views import interview_score

# Create your views here.
@login_required
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
    interview_ = get_object_or_404(Interview,interview_id=interview_id)
    interview_.status = 'in_progress'
    interview_.started_at = timezone.now()
    interview_.save()

    questions = QuestionAndAnswer.objects.filter(interview_id=interview_id).order_by('order_no').values('question_id','question')

    all_questions = {}
    for i,question in enumerate(questions):
        all_questions[i+1] = {'question':question['question'],"question_id":str(question['question_id'])}

    # print(questions)
    # print(all_questions)
    context = {'questions':all_questions,'interview_id':interview_.interview_id}
    return render(request, 'interview.html',context)

def result(request,interview_id):
    if request.method == 'POST':
        groq = Groq(api_key=settings.GROQ_API_KEY)

        audio_files = request.FILES.getlist('audio_files')
        question_id = request.POST.getlist('question_ids')
        question_text = request.POST.getlist('question_text')
        transcriptions = []
        for i,audio_file in enumerate(audio_files):
            response = groq.audio.transcriptions.create(file=(audio_file.name,audio_file.read()),
                                                    model='whisper-large-v3-turbo')
            question = get_object_or_404(QuestionAndAnswer, question_id=question_id[i])
            question.audio = audio_file.read()
            question.answer_audio_transcript = response.text
            transcriptions.append(question)
            question.save()

        interview_ = get_object_or_404(Interview, interview_id=interview_id)
        interview_.finished_at = timezone.now()
        interview_.save()

        if interview_.status == 'in_progress':
            answer_evaluation(interview_id)

        return JsonResponse({"test":'123'},content_type="application/json")

def result_page(request,interview_id):
    interview_ = get_object_or_404(Interview, interview_id=interview_id)
    if interview_.status == 'completed':
        questions = QuestionAndAnswer.objects.filter(interview_id=interview_id)

        scores = interview_score(interview_id)

        context = {
            'status': 'in_progress',
            'questions': questions,
            'interview': interview_,
        }
        context.update(scores)
    else:
        context = {}
    return render(request,'interview_result.html',context)

def question_result(request, question_id):
    question = get_object_or_404(QuestionAndAnswer, question_id=question_id)

    context = {
        'question': question,
        'report': question.analysis_json,
    }
    return render(request,'question_result.html',context)