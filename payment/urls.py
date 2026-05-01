from django.urls import path
from payment.views import *
urlpatterns = [
    path('checkout/<plan_id>', checkout, name='checkout'),
    path("process_order/<plan_id>", process_order, name='process_order'),
    path('verify_payment', payment_verify, name='payment_verify'),
    path('payment_success/<str:payment_id>/', payment_success, name='payment_success'),
]