from django.contrib import admin

from payment.models import *
# Register your models here.
admin.site.register(Payment)
admin.site.register(Transaction)
admin.site.register(Wallet)

class PlanAdmin(admin.ModelAdmin):
    model = Plan
    readonly_fields = ['plan_id']

admin.site.register(Plan, PlanAdmin)
admin.site.register(Vendor)
admin.site.register(Coupon)