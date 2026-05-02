import json
import os

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.urls import reverse
from django.db import transaction

from payment.models import *
from dotenv import load_dotenv

from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta

load_dotenv()
# Create your views here.

Cashfree.XClientId = settings.CASHFREE_CLIENT_ID
Cashfree.XClientSecret = settings.CASHFREE_CLIENT_SECRET
Cashfree.XEnvironment = Cashfree.SANDBOX
x_api_version = "2023-08-01"


def calculate_total_charge(product_price, cashfree_fee_pct, gst_pct):
    # Effective Cashfree fee including GST
    fee_rate = cashfree_fee_pct * (1 + gst_pct)

    # Adjust final charge so you still receive product_price after fees
    total_charge = product_price / (1 - fee_rate)

    return round(total_charge, 2)


@login_required
def checkout(request, plan_id):
    plan = Plan.objects.get(plan_id=plan_id)

    total_amount = calculate_total_charge(product_price=plan.amount, cashfree_fee_pct=0.018, gst_pct=0.18)
    env = os.environ.get('ENVIRONMENT')
    if env == "production":
        env_ = 'production'
    else:
        env_ = 'sandbox'

    context = {
        'plan': plan,
        'total_amount': total_amount,
        'extra_fee': round(total_amount - plan.amount, 2),
        'env': env_,
    }
    return render(request, 'checkout.html', context)


def process_order(request, plan_id):
    plan = Plan.objects.get(plan_id=plan_id)
    payment = Payment.objects.create(
        user=request.user,
        plan=plan,
        amount_paid=plan.amount,
        is_paid=False
    )

    total_amount = calculate_total_charge(plan.amount, cashfree_fee_pct=0.018, gst_pct=0.18)

    if os.environ.get("ENVIRONMENT") == "production":
        callback_url = OrderMeta(
            return_url=request.build_absolute_uri(
                reverse(settings.CASHFREE_CALLBACK_URL)) + "?order_id={order_id}".replace("http://",
                                                                                          "https://")
        )
    else:
        callback_url = OrderMeta(
            return_url=request.build_absolute_uri(reverse(settings.CASHFREE_CALLBACK_URL)) + "?order_id={order_id}")

    customer = CustomerDetails(
        customer_id=f"user_{request.user.username}",
        customer_name=request.user.username,
        customer_phone='9171000008',
        customer_email=request.user.email
    )

    data = CreateOrderRequest(
        order_id=str(payment.payment_id),
        order_amount=float(total_amount),  # RUPEES
        order_currency="INR",
        customer_details=customer,
        order_meta=callback_url,
    )

    response = Cashfree(XEnvironment=Cashfree.XEnvironment).PGCreateOrder(
        x_api_version,
        data,
        None,
        None
    )

    return JsonResponse({"payment_session_id": response.data.payment_session_id})


@csrf_exempt
def payment_verify(request):
    cashfree_order_id = request.GET.get("order_id")

    # 1️⃣ Validate request
    if not cashfree_order_id:
        return render(request, "payment_verify.html", {
            "status": "Invalid request",
            "is_success": False,
        })

    # 2️⃣ Fetch order
    try:
        order = Payment.objects.select_related("user", "plan").get(payment_id=cashfree_order_id)
    except Payment.DoesNotExist:
        return redirect('payment_success', payment_id=cashfree_order_id, )

    # 3️⃣ Verify with Cashfree
    response = Cashfree(XEnvironment=Cashfree.XEnvironment).PGFetchOrder(
        x_api_version,
        cashfree_order_id,
        None
    )

    # print("Cashfree Response:", response.data)

    if response.data.order_status != "PAID":
        return redirect('payment_success', payment_id=cashfree_order_id, )

    # 4️⃣ Prevent duplicate crediting
    if order.is_paid:
        return redirect('payment_success', payment_id=cashfree_order_id, )

    # 5️⃣ Atomic transaction (CRITICAL)
    with transaction.atomic():

        # Lock wallet row
        wallet = Wallet.objects.get(user=order.user)

        # Mark order paid
        order.is_paid = True
        order.signature_id = response.data.cf_order_id
        order.save()

        # Add credits to wallet
        wallet.interview_credits += order.plan.interview_credits
        wallet.resume_credits += order.plan.resume_credits
        wallet.save()

        # Log transactions (important for tracking)
        Transaction.objects.create(
            user=order.user,
            credits=order.plan.interview_credits,
            transaction_type="credit",
            category="interview"
        )

        Transaction.objects.create(
            user=order.user,
            credits=order.plan.resume_credits,
            transaction_type="credit",
            category="resume"
        )

    # 6️⃣ Success response
    return redirect('payment_success', payment_id=cashfree_order_id, )


def payment_success(request, payment_id):
    payment = Payment.objects.get(payment_id=payment_id)
    user_wallet = Wallet.objects.get(user=request.user)
    is_success = False

    if payment.is_paid:
        msg = 'Payment Verified & Credits Added'
        is_success = True
    else:
        msg = 'Payment Failed'

    context = {
        'status': msg,
        'order_id': payment_id,
        'is_success': is_success,
        'payment': payment,
        'user_wallet': user_wallet,
    }
    return render(request, "payment_success.html", context)


@login_required
def vendor_page(request):
    try:
        vendor = get_object_or_404(Vendor, user=request.user)
        coupon_codes = Coupon.objects.filter(vendor=vendor)

        context = {
            'coupon_codes': coupon_codes,
        }
        return render(request, "vendor_page.html", context)
    except Vendor.DoesNotExist:
        return redirect('home')


def generate_coupon(request):
    data = json.loads(request.body)
    plan_id = data.get("plan_id")
    plan = Plan.objects.get(plan_id=plan_id)
    vendor = Vendor.objects.get(user=request.user)
    is_token_limited = False

    # vendor keys verification and key reduce
    if plan.name == 'interviewer':
        if vendor.interviewer_plan_keys <= 0:
            is_token_limited = True
        else:
            vendor.interviewer_plan_keys -= 1

    elif plan.name == 'resume analyer':
        if vendor.resume_plan_keys <= 0:
            is_token_limited = True
        else:
            vendor.resume_plan_keys -= 1

    elif plan.name == 'pro':
        if vendor.pro_plan_keys <= 0:
            is_token_limited = True
        else:
            vendor.pro_plan_keys -= 1

    if vendor and vendor.is_active and not is_token_limited:
        coupon = Coupon.objects.create(
            plan=plan,
            vendor=vendor,
        )
        vendor.save()
        context = {
            'success': True,
            'code': coupon.coupon_id,
        }
    elif is_token_limited:
        context = {
            'success': False,
            'data': "You don't enough coupons",
        }
    else:
        context = {'data': None, 'success': False}

    return JsonResponse(context)


def coupon_page(request):
    return render(request, 'coupon_redeem.html')



def apply_coupon(request):
    data = json.loads(request.body)
    coupon_id = data.get("coupon_id")

    try:
        coupon = Coupon.objects.get(coupon_id=coupon_id)
    except Coupon.DoesNotExist:
        return JsonResponse({'success': False, 'data': "Coupon does not exist"})

    wallet = Wallet.objects.get(user=request.user)

    if not coupon.claimed_user:
        coupon.claimed_user = request.user
        wallet.interview_credits += coupon.plan.interview_credits
        wallet.resume_credits += coupon.plan.resume_credits
        wallet.save()
        coupon.save()
        context = {
            'success': True,
            'code': coupon.coupon_id,
            'wallet': {
                'interview_credits': wallet.interview_credits,
                'resume_credits': wallet.resume_credits,
            },

            'coupon': {
                'id': coupon.coupon_id,
                'plan_name': coupon.plan.name,
                'interview_credits': coupon.plan.interview_credits,
                'resume_credits': coupon.plan.resume_credits,
            }
        }
    else:
        context = {
            'success': False,
            'data': "You coupon already redeemed ",
        }

    return JsonResponse(context)
