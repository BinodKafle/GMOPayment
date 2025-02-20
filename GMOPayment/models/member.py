from django.db import models
from django.core.validators import MinLengthValidator

from GMOPayment.models.base import BaseModel, ContactInfoMixin


class Member(BaseModel, ContactInfoMixin):
    member_id = models.CharField(max_length=50, unique=True, validators=[MinLengthValidator(5)])
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name or self.member_id

