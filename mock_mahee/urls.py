from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'schedules', views.ScheduleViewSet)

urlpatterns = [
    # Interview endpoints: api/interviews/...
    path('api/interviews/', include(router.urls)),
    path('api/interviews/dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # Question endpoints: api/questions/...
    path('api/questions/generate-questions/', views.QuestionGenerationView.as_view(), name='generate_questions'),

    # Resume endpoints: api/resumes/...
    path('api/resumes/analyze-resume/', views.analyze_resume, name='analyze_resume'),
    path('api/resumes/analyze-and-generate-questions/', views.analyze_and_generate_questions, name='analyze_and_generate_questions'),

    # Shortlisting endpoints: api/shortlisting/...
    path('api/shortlisting/shortlist/', views.shortlist_candidate, name='shortlist_candidate'),

    # STT endpoints: api/stt/...
    path('api/stt/transcribe-audio/', views.transcribe_audio, name='transcribe_audio'),

    # TTS endpoints: api/tts/...
    path('api/tts/generate-audio/', views.generate_audio, name='generate_audio'),
]
