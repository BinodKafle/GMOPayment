from rest_framework import generics, status
from rest_framework.response import Response

from GMOPayment.models.payment_method import PaymentMethod
from GMOPayment.serializers.payment_method import PaymentMethodSerializer
from GMOPayment.services.payment_method import GMOPaymentMethodService


class PaymentMethodListCreateView(generics.ListCreateAPIView):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    service = GMOPaymentMethodService()

    def create(self, request, *args, **kwargs):
        response = self.service.save_card(
            request.data["member_id"], request.data["card_no"], request.data["expire"], request.data.get("security_code")
        )
        return Response(response, status=status.HTTP_201_CREATED)
