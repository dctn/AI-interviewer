from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from core.forms import *
from core.models import *
from core.resume_analysis import llm_resume_analysis
import numpy as np
from interview.models import *
from payment.models import *

# Create your views here.
def interview_score(interview_id):
    questions = QuestionAndAnswer.objects.filter(interview_id=interview_id)

    overall_score = 0
    communication = 0
    depth = 0
    clarity = 0
    completeness = 0
    technical_accuracy = 0
    relevance = 0
    verdict = []
    for question in questions:
        overall_score += question.analysis_json['overall_score']
        communication += question.analysis_json['communication']
        depth += question.analysis_json['depth']
        clarity += question.analysis_json['clarity']
        completeness += question.analysis_json['completeness']
        technical_accuracy += question.analysis_json['technical_accuracy']
        relevance += question.analysis_json['relevance']
        verdict.append(question.analysis_json.get('final_verdict', 'unknown'))

    verdict_np = np.array(verdict)

    scores = {
        'overall_score': overall_score / len(questions),
        'communication': communication / len(questions),
        'depth': depth / len(questions),
        'clarity': clarity / len(questions),
        'completeness': completeness / len(questions),
        'technical_accuracy': technical_accuracy / len(questions),
        'relevance': relevance / len(questions),
        'verdict': verdict_np[verdict_np.argmax()]
    }
    return scores

def cheating(request):
    return render(request, "index.html")

def home(request):
    return render(request, "landing_page.html")

@login_required
def dashboard(request):
    user_data = ResumeAnalysis.objects.filter(user_id=request.user)
    interview_data = Interview.objects.filter(user_id=request.user,status__exact='completed')
    user_wallet = get_object_or_404(Wallet, user=request.user)

    interview_scores = []

    for interview in interview_data:
        scores = interview_score(interview.interview_id)
        interview_scores.append({
            'overall_score':scores['overall_score'],
            'relevance':scores['relevance'],
            'verdict':scores['verdict'],
            'category': interview.resume.name,
            'interview_id': interview.interview_id,
            'completed_at':interview.finished_at,
        })

    context = {"user_data":user_data,
               "interview_data":interview_data,
               'interview_scores':interview_scores,
               'wallet':user_wallet,}
    # print(interview_scores)
    return render(request, "dashboard.html",context)

@login_required
def resume_analysis(request):
    user_wallet = get_object_or_404(Wallet, user=request.user)
    credit_status = None

    if request.method == "POST" and user_wallet.resume_credits >= 1:
        form = ResumeForm(request.POST,request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.user_id = request.user
            data.save()

            user_wallet.resume_credits -= 1
            user_wallet.save()

            result,jd = llm_resume_analysis(data.resume.path,data.jd)
            # print(data.resume,data.jd)
            data.jd = jd
            data.report = result

            data.save()
            return redirect('resume_result',data.analysis_id)
    else:
        if user_wallet.resume_credits <= 0:
            credit_status = 'insufficient_credits'
        form = ResumeForm()

    context = {"form":form,'credit_status': credit_status}
    return render(request,'resume_analysis.html',context)

def resume_result(request,analysis_id):
    data = get_object_or_404(ResumeAnalysis, pk=analysis_id)
    return render(request,'resume_analysis.html',{'result':data.report})

