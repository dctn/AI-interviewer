from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from core.forms import *
from core.models import *
from core.resume_analysis import llm_resume_analysis
import json
# Create your views here.

def cheating(request):
    return render(request, "index.html")

def home(request):
    return render(request, "landing_page.html")

def dashboard(request):
    user_data = ResumeAnalysis.objects.filter(user_id=request.user)
    context = {"user_data":user_data}
    # print(user_data)
    return render(request, "dashboard.html",context)
@login_required
def resume_analysis(request):
    if request.method == "POST":
        form = ResumeForm(request.POST,request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.user_id = request.user
            data.save()

            result,jd = llm_resume_analysis(data.resume.path,data.jd)
            # print(data.resume,data.jd)
            data.jd = jd
            data.report = result

            data.save()
            return redirect('resume_result',data.analysis_id)
    else:
        form = ResumeForm()

    context = {"form":form}
    return render(request,'resume_analysis.html',context)

def resume_result(request,analysis_id):
    data = get_object_or_404(ResumeAnalysis, pk=analysis_id)
    return render(request,'resume_analysis.html',{'result':data.report})

