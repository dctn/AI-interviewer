from django.contrib import admin

from interview.models import Interview, QuestionAndAnswer

# Register your models here.
class InterviewAdmin(admin.ModelAdmin):
    model = Interview
    # fields = ['interview_id']
    readonly_fields = ['interview_id']


admin.site.register(Interview, InterviewAdmin)

class QuestionAdmin(admin.ModelAdmin):
    model = QuestionAndAnswer
    list_display = ['question','question_domain','category','order_no',]
    search_fields = ['interview__user__username','question_id','interview__interview_id']
    sortable_by = ['order_no']

admin.site.register(QuestionAndAnswer, QuestionAdmin)