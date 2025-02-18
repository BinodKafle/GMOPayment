from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.payment import PaymentService

class CreatePaymentView(APIView):
    def post(self, request):
        amount = request.data.get("amount")
        order_id = request.data.get("order_id")
        if not amount or not order_id:
            return Response(
                {"error": "Amount and Order ID are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = PaymentService()
        try:
            result = service.create_payment(amount, order_id)
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PaymentStatusView(APIView):
    def get(self, request, payment_id):
        service = PaymentService()
        try:
            result = service.get_payment_status(payment_id)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
