from django.db import models
from django.core.validators import EmailValidator


class Schedule(models.Model):
    candidate_name = models.CharField(max_length=200)
    email = models.EmailField(validators=[EmailValidator()])
    role = models.CharField(max_length=100)
    interview_date = models.CharField(max_length=20)
    interview_time = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate_name} - {self.role}"

    class Meta:
        db_table = 'schedules'
