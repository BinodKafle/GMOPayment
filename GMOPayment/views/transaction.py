from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from GMOPayment.services.transaction import GMOTransactionService


class TransactionCreateView(APIView):
    service = GMOTransactionService()

    def post(self, request, *args, **kwargs):
        order_id = request.data.get("order_id")
        card_token = request.data.get("card_token")
        if not order_id:
            raise ValidationError("Order ID is required.")
        if not card_token:
            raise ValidationError("Card token is required.")
        response = self.service.create_transaction_with_new_payment_method(order_id, card_token, )
        return Response(response, status=status.HTTP_201_CREATED)


class Finalize3dsPaymentView(APIView):
    service = GMOTransactionService()

    def post(self, request, *args, **kwargs):
        access_id = request.data.get("access_id")
        if not access_id:
            raise ValidationError("access_id is required.")
        response = self.service.finalize_3d_secure_payment(access_id)
        return Response(response, status=status.HTTP_200_OK)


class TransactionOrderUpdateView(APIView):
    service = GMOTransactionService()

    def post(self, request, *args, **kwargs):
        access_id = request.data.get("access_id")
        amount = request.data.get("amount")
        if not access_id:
            raise ValidationError("access_id is required.")
        if not amount:
            raise ValidationError("amount is required.")
        response = self.service.update_order(access_id, amount)
        return Response(response, status=status.HTTP_200_OK)


class TransactionOrderCaptureView(APIView):
    service = GMOTransactionService()

    def post(self, request, *args, **kwargs):
        access_id = request.data.get("access_id")
        if not access_id:
            raise ValidationError("access_id is required.")
        response = self.service.capture_transaction(access_id)
        return Response(response, status=status.HTTP_200_OK)


class TransactionOrderCancelView(APIView):
    service = GMOTransactionService()

    def post(self, request, *args, **kwargs):
        access_id = request.data.get("access_id")
        if not access_id:
            raise ValidationError("access_id is required.")
        response = self.service.cancel_transaction(access_id)
        return Response(response, status=status.HTTP_200_OK)


class TransactionOrderInqueryView(APIView):
    service = GMOTransactionService()

    def post(self, request, *args, **kwargs):
        access_id = request.data.get("access_id")
        if not access_id:
            raise ValidationError("access_id is required.")
        response = self.service.inquiry_transaction_order(access_id)
        return Response(response, status=status.HTTP_200_OK)