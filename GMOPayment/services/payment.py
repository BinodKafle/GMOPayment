import logging
from typing import Dict, Any

from GMOPayment.client import get_client
from GMOPayment.exceptions import GMOAPIError


class PaymentService:
    def __init__(self):
        self.client = get_client()

    def create_payment(self, amount: float, order_id: str) -> Dict[str, Any]:
        endpoint = "payments/create"
        payload = {
            "amount": amount,
            "order_id": order_id,
        }
        try:
            return self.client.post(endpoint, payload)
        except GMOAPIError as e:
            logging.error(f"Failed to create payment: {e}")
            raise

    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        endpoint = f"payments/{payment_id}/status"
        try:
            return self.client.get(endpoint)
        except GMOAPIError as e:
            logging.error(f"Failed to fetch payment status: {e}")
            raise
