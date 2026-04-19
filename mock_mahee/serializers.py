from rest_framework import serializers
from .models import Schedule


# ==================== Interview Serializers ====================

class ScheduleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['candidate_name', 'email', 'role', 'interview_date', 'interview_time', 'status']


class ScheduleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['candidate_name', 'email', 'role', 'interview_date', 'interview_time', 'status']


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'


# ==================== Question Serializers ====================

class ReferenceItemSerializer(serializers.Serializer):
    source = serializers.CharField()
    snippet = serializers.CharField()


class QuestionItemSerializer(serializers.Serializer):
    question_no = serializers.IntegerField(min_value=1)
    question = serializers.CharField(min_length=5)
    topic = serializers.CharField(min_length=2)
    category = serializers.CharField(default='technical')
    difficulty = serializers.ChoiceField(choices=['easy', 'medium', 'hard'])
    time_limit_sec = serializers.IntegerField(min_value=30, max_value=600)
    expected_points = serializers.ListField(child=serializers.CharField(), min_length=1)
    resume_reference = ReferenceItemSerializer(required=False)
    jd_reference = ReferenceItemSerializer(required=False)


class QuestionGenerationRequestSerializer(serializers.Serializer):
    role = serializers.CharField(min_length=2)
    job_description = serializers.CharField(min_length=10)
    resume_text = serializers.CharField(min_length=10)
    question_count = serializers.IntegerField(default=5, min_value=1, max_value=10)
    difficulty = serializers.ChoiceField(choices=['easy', 'medium', 'hard'], default='medium')


class QuestionGenerationResponseSerializer(serializers.Serializer):
    questions = QuestionItemSerializer(many=True)


# ==================== Resume Serializers ====================

class ResumeAnalysisResponse(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.CharField()
    phone = serializers.CharField()
    summary = serializers.CharField()
    skills = serializers.ListField(child=serializers.CharField())
    projects = serializers.ListField(child=serializers.CharField())
    education = serializers.ListField(child=serializers.CharField())
    experience = serializers.ListField(child=serializers.CharField())
    certifications = serializers.ListField(child=serializers.CharField())
    raw_text = serializers.CharField()


class AnalyzeAndGenerateResponse(serializers.Serializer):
    resume_analysis = ResumeAnalysisResponse()
    generated_questions = serializers.JSONField()


# ==================== Shortlisting Serializers ====================

class ResumeAnalysisInput(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.CharField()
    phone = serializers.CharField()
    summary = serializers.CharField()
    skills = serializers.ListField(child=serializers.CharField())
    projects = serializers.ListField(child=serializers.CharField())
    education = serializers.ListField(child=serializers.CharField())
    experience = serializers.ListField(child=serializers.CharField())
    certifications = serializers.ListField(child=serializers.CharField())
    raw_text = serializers.CharField()


class ShortlistRequest(serializers.Serializer):
    role = serializers.CharField()
    job_description = serializers.CharField()
    resume_analysis = ResumeAnalysisInput()


class ShortlistResponse(serializers.Serializer):
    candidate_name = serializers.CharField()
    email = serializers.CharField()
    role = serializers.CharField()
    shortlist_status = serializers.CharField()
    score = serializers.FloatField()
    matching_skills = serializers.ListField(child=serializers.CharField())
    missing_skills = serializers.ListField(child=serializers.CharField())
    feedback = serializers.CharField()
    schedule = serializers.JSONField(required=False)


# ==================== STT Serializers ====================

class STTResponse(serializers.Serializer):
    message = serializers.CharField()
    transcript = serializers.CharField()
    file_name = serializers.CharField()


# ==================== TTS Serializers ====================

class TTSRequest(serializers.Serializer):
    text = serializers.CharField()
    voice = serializers.CharField(default='default')
    file_name = serializers.CharField(default='question_audio')


class TTSResponse(serializers.Serializer):
    message = serializers.CharField()
    audio_url = serializers.CharField()
    file_name = serializers.CharField()
