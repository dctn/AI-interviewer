from django.urls import path, include
from core.views import *
urlpatterns = [
    path("",index,name="index"),
    path('home/',home,name="home"),
]