from django.urls import path, include
from core.views import *
urlpatterns = [
    path("cheating/",cheating,name="index"),
    path('',home,name="home"),
    path('resume_analysis/',resume_analysis,name="resume_analysis"),
    path('result/<analysis_id>',resume_result,name="resume_result"),
    path('dashboard/',dashboard,name="dashboard"),
]