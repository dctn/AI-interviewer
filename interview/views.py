from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from langchain_groq import ChatGroq
from groq import Groq

from django.conf import settings
# Create your views here.
def interview(request):
    return render(request, 'interview.html')

def result(request):
    if request.method == 'POST':
        groq = Groq(api_key=settings.GROQ_API_KEY)

        audio_file = request.FILES.getlist('audio_files')
        question_id = request.POST.getlist('question_ids')
        question_text = request.POST.getlist('question_text')

        for i,audio_file in enumerate(audio_file):
            response = groq.audio.transcriptions.create(file=(audio_file.name,audio_file.read()),
                                                    model='whisper-large-v3-turbo')
            print(response)
        return JsonResponse({"test":'123'},content_type="application/json")