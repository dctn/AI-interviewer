from django.urls import path
from interview.views import *

urlpatterns = [
    path('',interview,name='interview'),
    path('result/',result,name='result'),
]