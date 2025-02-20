from rest_framework import generics, status
from rest_framework.response import Response

from GMOPayment.models.merchant import Merchant
from GMOPayment.serializers.merchant import MerchantSerializer
from GMOPayment.services.merchant import GMOMerchantService


class MerchantViewSet(generics.ListAPIView, generics.CreateAPIView):
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    service = GMOMerchantService()

    def create(self, request, *args, **kwargs):
        response = self.service.create_merchant_account(request.data["member_id"], request.data.get("name"))
        return Response(response, status=status.HTTP_201_CREATED)
