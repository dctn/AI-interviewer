import os
import shutil
import uuid
import json
from datetime import datetime, timedelta

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Count

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Schedule
from .serializers import (
    ScheduleSerializer, ScheduleCreateSerializer, ScheduleUpdateSerializer,
    QuestionGenerationRequestSerializer,
    ResumeAnalysisResponse, AnalyzeAndGenerateResponse,
    ShortlistRequest, ShortlistResponse,
    STTResponse,
    TTSResponse,
)


# ==================== Interview Views ====================

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return ScheduleCreateSerializer
        if self.action in ['update', 'partial_update']:
            return ScheduleUpdateSerializer
        return ScheduleSerializer

    @action(detail=False, methods=['post'])
    def auto_schedule(self, request):
        payload = request.data
        # Auto-scheduling logic from FastAPI
        total_schedules = Schedule.objects.count()
        slots_per_day = 8
        slot_duration_minutes = 30
        start_hour = 10
        start_minute = 0

        day_offset = total_schedules // slots_per_day
        slot_index = total_schedules % slots_per_day

        base_date = datetime.now().date() + timedelta(days=1 + day_offset)

        slot_start_time = datetime.combine(base_date, datetime.min.time()).replace(
            hour=start_hour, minute=start_minute
        ) + timedelta(minutes=slot_index * slot_duration_minutes)

        schedule = Schedule.objects.create(
            candidate_name=payload['candidate_name'],
            email=payload['email'],
            role=payload['role'],
            interview_date=slot_start_time.strftime('%Y-%m-%d'),
            interview_time=slot_start_time.strftime('%I:%M %p'),
            status='scheduled'
        )
        serializer = ScheduleSerializer(schedule)
        return Response({
            'message': 'Candidate auto-scheduled successfully',
            'schedule': serializer.data
        })


class DashboardView(APIView):
    def get(self, request):
        total = Schedule.objects.count()
        scheduled = Schedule.objects.filter(status='scheduled').count()
        completed = Schedule.objects.filter(status='completed').count()
        cancelled = Schedule.objects.filter(status='cancelled').count()

        upcoming = Schedule.objects.filter(status='scheduled').order_by('interview_date', 'interview_time')

        completed_list = Schedule.objects.filter(status='completed').order_by('-interview_date', '-interview_time')

        return Response({
            'summary': {
                'total_interviews': total,
                'scheduled_interviews': scheduled,
                'completed_interviews': completed,
                'cancelled_interviews': cancelled
            },
            'upcoming': ScheduleSerializer(upcoming, many=True).data,
            'completed': ScheduleSerializer(completed_list, many=True).data
        })


# ==================== Question Views ====================

class QuestionGenerationView(APIView):
    def post(self, request):
        serializer = QuestionGenerationRequestSerializer(data=request.data)
        if serializer.is_valid():
            from .utils.question_pipeline import run_question_generation_pipeline
            from .utils.question_schemas import QuestionGenerationRequest
            request_obj = QuestionGenerationRequest(**serializer.validated_data)
            result = run_question_generation_pipeline(request_obj)
            return Response(result.model_dump(), status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================== Resume Views ====================

UPLOAD_DIR = "media/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@csrf_exempt
@require_http_methods(["POST"])
def analyze_resume(request):
    try:
        if not request.FILES.get('file'):
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        file = request.FILES['file']
        if not file.name.lower().endswith('.pdf'):
            return JsonResponse({'error': 'Only PDF files allowed'}, status=400)

        file_path = os.path.join(UPLOAD_DIR, file.name)
        with open(file_path, 'wb') as buffer:
            for chunk in file.chunks():
                buffer.write(chunk)

        # Reuse pipeline
        from .utils.resume_pipeline import run_resume_analysis_pipeline
        result = run_resume_analysis_pipeline(file_path)

        serializer = ResumeAnalysisResponse(result)
        return JsonResponse(serializer.data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def analyze_and_generate_questions(request):
    try:
        file = request.FILES.get('file')
        role = request.POST.get('role')
        job_description = request.POST.get('job_description')
        question_count = int(request.POST.get('question_count', 5))
        difficulty = request.POST.get('difficulty', 'medium')

        if not file:
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        if not file.name.lower().endswith('.pdf'):
            return JsonResponse({'error': 'Only PDF files allowed'}, status=400)

        file_path = os.path.join(UPLOAD_DIR, file.name)
        with open(file_path, 'wb') as buffer:
            for chunk in file.chunks():
                buffer.write(chunk)

        # Resume analysis
        from .utils.resume_pipeline import run_resume_analysis_pipeline
        resume_result = run_resume_analysis_pipeline(file_path)

        # Question generation
        from .utils.question_pipeline import run_question_generation_pipeline
        from .utils.question_schemas import QuestionGenerationRequest
        request_obj = QuestionGenerationRequest(
            role=role,
            job_description=job_description,
            resume_text=resume_result['raw_text'],
            question_count=question_count,
            difficulty=difficulty
        )
        questions_result = run_question_generation_pipeline(request_obj)

        data = {
            'resume_analysis': resume_result,
            'generated_questions': questions_result.model_dump()
        }

        serializer = AnalyzeAndGenerateResponse(data)
        return JsonResponse(serializer.data, safe=False)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'detail': str(e)}, status=400)


# ==================== Shortlisting Views ====================

@csrf_exempt
@require_http_methods(["POST"])
def shortlist_candidate(request):
    try:
        data = json.loads(request.body)
        serializer = ShortlistRequest(data=data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        payload = serializer.validated_data
        # Reuse service
        from .utils.shortlisting_service import perform_shortlisting
        result = perform_shortlisting(
            resume_analysis=payload['resume_analysis'],
            role=payload['role'],
            job_description=payload['job_description']
        )

        if result['shortlist_status'] == 'shortlisted':
            from .utils.database import auto_schedule_candidate_direct
            schedule_result = auto_schedule_candidate_direct(
                result['candidate_name'],
                result['email'],
                result['role']
            )
            result['schedule'] = schedule_result

        serializer_out = ShortlistResponse(result)
        return JsonResponse(serializer_out.data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==================== STT Views ====================

AUDIO_INPUT_DIR = "media/audio_inputs"
os.makedirs(AUDIO_INPUT_DIR, exist_ok=True)


@csrf_exempt
@require_http_methods(["POST"])
def transcribe_audio(request):
    try:
        file = request.FILES['file']
        extension = os.path.splitext(file.name)[1].lower()
        if extension not in ['.wav', '.mp3', '.m4a', '.ogg', '.webm']:
            return JsonResponse({'error': 'Invalid audio format'}, status=400)

        safe_file_name = f"{uuid.uuid4().hex}_{file.name}"
        file_path = os.path.join(AUDIO_INPUT_DIR, safe_file_name)

        with open(file_path, 'wb') as buffer:
            for chunk in file.chunks():
                buffer.write(chunk)

        from .utils.groq_stt_client import transcribe_audio_with_groq
        transcript = transcribe_audio_with_groq(file_path, safe_file_name)

        data = {
            'message': 'Audio transcribed successfully',
            'transcript': transcript,
            'file_name': safe_file_name
        }

        serializer = STTResponse(data)
        return JsonResponse(serializer.data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==================== TTS Views ====================

AUDIO_OUTPUT_DIR = "media/audio_outputs"
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)


@csrf_exempt
@require_http_methods(["POST"])
def generate_audio(request):
    try:
        from gtts import gTTS

        # Handle both JSON and form-encoded requests
        if request.content_type and 'application/json' in request.content_type:
            body = json.loads(request.body)
        else:
            body = request.POST

        text = body.get('text')
        file_name = body.get('file_name', 'question_audio')

        if not text:
            return JsonResponse({'error': 'No text provided'}, status=400)

        safe_file_name = f"{file_name}_{uuid.uuid4().hex[:8]}.mp3"
        output_path = os.path.join(AUDIO_OUTPUT_DIR, safe_file_name)

        tts = gTTS(text=text, lang='en')
        tts.save(output_path)

        audio_url = f"/media/audio_outputs/{safe_file_name}"

        response_data = {
            'message': 'Audio generated successfully',
            'audio_url': audio_url,
            'file_name': safe_file_name
        }

        serializer = TTSResponse(response_data)
        return JsonResponse(serializer.data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
