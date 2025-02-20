from rest_framework import serializers

from GMOPayment.models.transaction import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    job_cd_display = serializers.CharField(source='get_job_cd_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'
