from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator, MinLengthValidator
from uuid import uuid4
# Create your models here.

class ResumeAnalysis(models.Model):
    analysis_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/', validators=[FileExtensionValidator(['pdf'])])
    jd = models.TextField(validators=[
        MinLengthValidator(150,message='Job description must be at least 150 characters long'),
    ])
    report = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{str(self.user_id.username)}"

    def score(self):
        if self.report.get('overall_score') >= 80:
            return 'high'
        elif self.report.get('overall_score') >= 50:
            return 'medium'
        else:
            return 'low'