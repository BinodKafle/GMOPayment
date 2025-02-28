from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from GMOPayment.models.payment_method import PaymentMethod
from GMOPayment.serializers.payment_method import PaymentMethodSerializer
from GMOPayment.services.payment_method import GMOPaymentMethodService


class PaymentMethodListCreateView(generics.ListCreateAPIView):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    service = GMOPaymentMethodService()

    def create(self, request, *args, **kwargs):
        member_id = request.data.get("member_id")
        card_token = request.data.get("card_token")
        response = self.service.save_card(member_id, card_token)
        return Response(response, status=status.HTTP_201_CREATED)

class VerifyCard(APIView):
    service = GMOPaymentMethodService()

    def post(self, request, *args, **kwargs):
        member_id = request.data.get("member_id")
        card_token = request.data.get("card_token")
        response = self.service.verify_card(member_id, card_token)
        return Response(response, status=status.HTTP_200_OK)

class CardDetailsByToken(APIView):
    service = GMOPaymentMethodService()

    def post(self, request, *args, **kwargs):
        card_token = request.data.get("card_token")
        response = self.service.get_card_details_by_token(card_token)
        return Response(response, status=status.HTTP_200_OK)


class CardDetailsByMember(APIView):
    service = GMOPaymentMethodService()

    def post(self, request, *args, **kwargs):
        member_id = request.data.get("member_id")
        card_type = request.data.get("card_type")
        card_id = request.data.get("card_id")
        if not member_id:
            raise ValidationError("member_id is required.")
        if not card_type:
            raise ValidationError("card_type is required.")
        if not card_id:
            raise ValidationError("card_id is required.")
        response = self.service.get_card_details_by_member(member_id, card_type, card_id)
        return Response(response, status=status.HTTP_200_OK)

class CreateTokenView(APIView):
    service = GMOPaymentMethodService()

    def post(self, request, *args, **kwargs):
        card_no = request.data.get("card_number")
        card_holder_name = request.data.get("card_holder_name")
        expire_month = request.data.get("expire_month")
        expire_year = request.data.get("expire_year")
        security_code = request.data.get("security_code")

        response = self.service.create_token(card_no, card_holder_name, expire_month, expire_year, security_code)
        return Response(response, status=status.HTTP_201_CREATED)
