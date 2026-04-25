import uuid

from django.contrib.auth.models import User
from django.db import models
from django.core.validators import FileExtensionValidator, MinLengthValidator


# Create your models here.
STATUS_CHOICES = [
    ('created', 'Created'),              # setup done, not started
    ('in_progress', 'In Progress'),      # interview running
    ('processing', 'Processing'),        # audio → text + AI evaluation
    ('completed', 'Completed'),          # results ready
    ('failed', 'Failed'),                # something broke
]

DIFFICULTY_CHOICES = [
    ('easy', 'Easy'),          # basic / theory
    ('medium', 'Medium'),      # practical / applied
    ('hard', 'Hard'),          # deep / edge cases
]

EXPERIENCE_CHOICES = [
    ('fresher', 'Fresher (0 years)'),
    ('junior', '1–3 years'),
    ('mid', '3–5 years'),
    ('senior', '5+ years'),
]

class Interview(models.Model):
    interview_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/',validators=[FileExtensionValidator(['pdf'])])
    jd = models.TextField(validators=[MinLengthValidator(150)])
    started_at = models.DateTimeField(auto_now=False,blank=True,null=True)
    finished_at = models.DateTimeField(auto_now=False,blank=True,null=True)
    status = models.CharField(choices=STATUS_CHOICES,default='created',max_length=100)
    difficulty = models.CharField(choices=DIFFICULTY_CHOICES,default='easy',max_length=100)
    experience = models.CharField(choices=EXPERIENCE_CHOICES, default='fresher', max_length=100)
    llm_cost = models.PositiveIntegerField(default=0)
    credits_used = models.PositiveIntegerField(default=0)
    cheating_count = models.PositiveIntegerField(default=0)
    overall_cost = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=200,unique=True,blank=True,null=True)

    def __str__(self):
        return f"{str(self.user)}"

class QuestionAndAnswer(models.Model):
    question_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
    order_no = models.PositiveIntegerField(default=0)
    question = models.TextField()
    expected_answer = models.TextField(blank=True,null=True)
    answer_audio_file = models.FileField(upload_to='answers/',blank=True,null=True)
    answer_audio_transcript = models.TextField(blank=True,null=True)
    score = models.PositiveIntegerField(default=0)
    feedback = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    question_domain = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    analysis_json = models.JSONField(default=dict,blank=True,null=True)
    llm_cost = models.PositiveIntegerField(default=0)

