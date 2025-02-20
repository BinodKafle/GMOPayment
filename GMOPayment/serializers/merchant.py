from rest_framework import serializers

from GMOPayment.models.merchant import Merchant


class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = '__all__'
