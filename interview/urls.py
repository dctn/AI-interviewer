from django.urls import path
from interview.views import *

urlpatterns = [
    path('interview_setup/', interview_setup, name='interview_setup'),
    path('<interview_id>/',interview,name='interview'),
    path('result/',result,name='result'),
]