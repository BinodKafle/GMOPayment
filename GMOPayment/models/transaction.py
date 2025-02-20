from django.db import models

from GMOPayment.models.base import BaseModel
from GMOPayment.models.member import Member
from GMOPayment.models.merchant import Merchant
from GMOPayment.models.payment_method import PaymentMethod


class Transaction(BaseModel):
    TRANSACTION_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELED', 'Canceled'),
    ]
    JOB_CODE_CHOICES = [
        ('AUTH', 'Authorize'),
        ('SALES', 'Capture'),
        ('VOID', 'Cancel'),
        ('RETURN', 'Refund'),
        ('SAUTH', 'Secure Authorize')
    ]

    order_id = models.CharField(max_length=50, unique=True)
    access_id = models.CharField(max_length=50)
    access_pass = models.CharField(max_length=50)
    amount = models.PositiveIntegerField()
    tax = models.PositiveIntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='JPY')
    job_cd = models.CharField(max_length=10, choices=JOB_CODE_CHOICES)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='PENDING')
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True)
    merchant_account = models.ForeignKey(Merchant, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_date = models.DateTimeField(null=True, blank=True)
    error_code = models.CharField(max_length=10, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Transaction {self.order_id} - {self.get_status_display()}"

    def get_status_display(self):
        return dict(self.TRANSACTION_STATUS_CHOICES).get(self.status, "Unknown")
