import uuid

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Wallet(models.Model):
    wallet_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    resume_credits = models.PositiveIntegerField(default=0)
    interview_credits = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


TRANSACTION_TYPE_CHOICES = [
    ('credit','Credit'),
    ('debit','Debit'),
]

TRANSACTION_CATEGORY_CHOICES = [
    ('resume','Resume'),
    ('interview','Interview'),
]

class Transaction(models.Model):
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credits = models.PositiveIntegerField(default=0)
    transaction_type = models.CharField(max_length=255, choices=TRANSACTION_TYPE_CHOICES)
    category = models.CharField(max_length=255, choices=TRANSACTION_CATEGORY_CHOICES)
    transaction_at = models.DateTimeField(auto_now_add=True)


class Plan(models.Model):
    plan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    amount = models.PositiveIntegerField(default=0)
    interview_credits = models.PositiveIntegerField(default=0)
    resume_credits = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_paid = models.PositiveIntegerField(default=0)
    signature_id = models.CharField(max_length=255, default="")
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL,null=True)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(auto_now_add=True)

class Vendor(models.Model):
    vendor_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    resume_plan_keys = models.PositiveIntegerField(default=0)
    interviewer_plan_keys = models.PositiveIntegerField(default=0)
    pro_plan_keys = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)



class Coupon(models.Model):
    coupon_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    claimed_user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
