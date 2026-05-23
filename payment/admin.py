from django.contrib import admin

from payment.models import *
# Register your models here.
admin.site.register(Payment)
admin.site.register(Transaction)
admin.site.register(Wallet)

class PlanAdmin(admin.ModelAdmin):
    model = Plan


class CouponAdmin(admin.ModelAdmin):
    model = Coupon
    list_display = ['coupon_id','vendor','claimed_user','plan',]
    search_fields = ['coupon_id','vendor__user__username','claimed_user__username']
    sortable_by = ['created_at']



admin.site.register(Plan, PlanAdmin)
admin.site.register(Vendor)
admin.site.register(Coupon,CouponAdmin)