from rest_framework import generics, status
from rest_framework.response import Response

from GMOPayment.models.transaction import Transaction
from GMOPayment.serializers.transaction import TransactionSerializer
from GMOPayment.services.transaction import GMOTransactionService


class TransactionListCreateView(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    service = GMOTransactionService()

    def create(self, request, *args, **kwargs):
        response = self.service.create_transaction(
            request.data["order_id"], request.data["amount"], request.data.get("job_cd", "AUTH")
        )
        return Response(response, status=status.HTTP_201_CREATED)
