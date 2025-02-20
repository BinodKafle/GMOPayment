from django.core.validators import MinLengthValidator
from django.db import models

from GMOPayment.models.base import BaseModel, ContactInfoMixin


class Merchant(BaseModel, ContactInfoMixin):
    merchant_id = models.CharField(max_length=50, unique=True, validators=[MinLengthValidator(5)])
    name = models.CharField(max_length=255)
    site_id = models.CharField(max_length=50)
    shop_id = models.CharField(max_length=50)
    shop_password = models.CharField(max_length=100)

    def __str__(self):
        return self.name
