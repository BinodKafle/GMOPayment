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
        response = self.service.create_transaction_with_payment_method(order_id, card_token, )
        return Response(response, status=status.HTTP_201_CREATED)
