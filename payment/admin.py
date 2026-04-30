from django.contrib import admin

from payment.models import Payment, Transaction, Wallet

# Register your models here.
admin.site.register(Payment)
admin.site.register(Transaction)
admin.site.register(Wallet)