from django.forms import ModelForm
from core.models import *

class ResumeForm(ModelForm):
    class Meta:
        model = ResumeAnalysis
        fields = '__all__'
        exclude = ['user_id','report','analysis_id']