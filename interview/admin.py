from django.contrib import admin

from interview.models import Interview, QuestionAndAnswer

# Register your models here.
admin.site.register(Interview)

class QuestionAdmin(admin.ModelAdmin):
    model = QuestionAndAnswer
    list_display = ['question_domain','category']
    search_fields = ['interview__user__username']
    sortable_by = ['order_no']

admin.site.register(QuestionAndAnswer, QuestionAdmin)