from django import forms

from interview.models import Interview


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['resume','jd','difficulty','experience']