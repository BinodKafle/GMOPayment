from django.core.validators import MinLengthValidator
from django.db import models

from GMOPayment.models.base import BaseModel
from GMOPayment.models.member import Member


class PaymentMethod(BaseModel):
    CARD_BRAND_CHOICES = [
        ('VISA', 'Visa'),
        ('MC', 'MasterCard'),
        ('AMEX', 'American Express'),
        ('DISC', 'Discover'),
        ('JCB', 'JCB'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payment_methods')
    card_no = models.CharField(max_length=20, validators=[MinLengthValidator(13)])
    expire = models.CharField(max_length=6, validators=[MinLengthValidator(4)])  # Format: YYMM
    security_code = models.CharField(max_length=6, null=True, blank=True, validators=[MinLengthValidator(3)])
    cardholder_name = models.CharField(max_length=255, null=True, blank=True)
    brand = models.CharField(max_length=10, choices=CARD_BRAND_CHOICES, null=True, blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_brand_display()} - {self.card_no[-4:]}"

    def get_brand_display(self):
        return dict(self.CARD_BRAND_CHOICES).get(self.brand, "Unknown")
