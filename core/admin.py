from django.contrib import admin
from core.models import *
# Register your models here.


class ResumeAdmin(admin.ModelAdmin):
    model = ResumeAnalysis
    # list_display  = ['analysis_id',]

admin.site.register(ResumeAnalysis, ResumeAdmin)