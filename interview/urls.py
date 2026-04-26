from django.urls import path
from interview.views import *

urlpatterns = [
    path('interview_setup/', interview_setup, name='interview_setup'),
    path('result/<interview_id>',result,name='result'),
    path('result_page/<interview_id>/',result_page,name='result_page'),
    path('<interview_id>/',interview,name='interview'),
    path('question_result/<question_id>',question_result,name='question_result'),
]