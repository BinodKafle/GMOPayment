import logging
from typing import Any

from ..gmo_client import GMOHttpClient
from GMOPayment.exceptions import GMOAPIException

logger = logging.getLogger(__name__)

class GMOTransactionService:
    def __init__(self):
        self.client = GMOHttpClient()

    def create_transaction_with_new_payment_method(self, order_id: int, card_token: str) -> dict[str, Any]:
        """Creates a transaction equivalent in GMO (EntryTran)."""
        payload = {
              "merchant": {
                "name": "Binod Test Store",
                "nameKana": "ジーエムオーストア",
                "nameAlphabet": "Sample Store",
                "nameShort": "サンプル",
                "contactName": "サポート窓口",
                "contactEmail": "support@example.com",
                "contactUrl": "https://example.com/contact",
                "contactPhone": "0120-123-456",
                "contactOpeningHours": "10:00-18:00",
                "callbackUrl": "https://example.com/callback",
                "webhookUrl": "https://example.com/webhook",
                "csrfToken": "bdb04c5f-42f0-29e2-0979-edae3e7760bf"
              },
              "order": {
                "orderId": order_id,
                "amount": "1000",
                "currency": "JPY",
                "clientFields": {
                  "clientField1": "Test 1",
                },
                "items": [
                  {
                    "name": "コーヒー豆",
                    "description": "service_title",
                    "quantity": 1,
                    "type": "SERVICE",
                    "price": "10",
                    "category": "7996", # https://github.com/greggles/mcc-codes/blob/main/mcc_codes.json#L8427C13-L8427C17
                    "productId": "service_id",
                  }
                ],
                "transactionType": "MIT",
              },
              "payer": {
                "name": "buyer_name",
                "nameKana": "ミホン　タロウ",
                "nameAlphabet": "Taro Mihon",
                "gender": "MALE",
                "dateOfBirth": "19950308",
                "email": "example@example.com",
                "accountId": "user_id",
                "ip": "172.16.0.1",
                "deviceType": "MOBILE_APP",
                "osType": "IOS",
                "httpUserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
              },
              "creditInformation": {
                "tokenizedCard": {
                  "type": "MP_TOKEN",
                  "token": card_token
                },
                "creditChargeOptions": {
                  "authorizationMode": "AUTH",
                  "useTds2": True,
                  "useFraudDetection": True,
                  "paymentMethod": "ONE_TIME",
                }
              }
            }

        try:
            response = self.client.post("credit/charge", payload)
            logger.info(f"Successfully created transaction for order: {order_id}")
            return response
        except GMOAPIException as e:
            logger.error(f"Failed to create transaction for order {order_id}: {e!s}")
            raise

    def create_transaction_with_registered_payment_method(self, order_id: int, member_id: str, card_id: str) -> dict[str, Any]:
        """Creates a transaction equivalent in GMO (EntryTran)."""
        payload = {
              "merchant": {
                "name": "Binod Test Store",
                "nameKana": "ジーエムオーストア",
                "nameAlphabet": "Sample Store",
                "nameShort": "サンプル",
                "contactName": "サポート窓口",
                "contactEmail": "support@example.com",
                "contactUrl": "https://example.com/contact",
                "contactPhone": "0120-123-456",
                "contactOpeningHours": "10:00-18:00",
                "callbackUrl": "https://example.com/callback",
                "webhookUrl": "https://example.com/webhook",
                "csrfToken": "bdb04c5f-42f0-29e2-0979-edae3e7760bf"
              },
              "order": {
                "orderId": order_id,
                "amount": "1000",
                "currency": "JPY",
                "clientFields": {
                  "clientField1": "Test 1",
                },
                "items": [
                  {
                    "name": "コーヒー豆",
                    "description": "service_title",
                    "quantity": 1,
                    "type": "SERVICE",
                    "price": "10",
                    "category": "7996", # https://github.com/greggles/mcc-codes/blob/main/mcc_codes.json#L8427C13-L8427C17
                    "productId": "service_id",
                  }
                ],
                "transactionType": "MIT",
              },
              "payer": {
                "name": "buyer_name",
                "nameKana": "ミホン　タロウ",
                "nameAlphabet": "Taro Mihon",
                "gender": "MALE",
                "dateOfBirth": "19950308",
                "email": "example@example.com",
                "accountId": "user_id",
                "ip": "172.16.0.1",
                "deviceType": "MOBILE_APP",
                "osType": "IOS",
                "httpUserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
              },
              "creditOnfileInformation": {
                "onfileCard": {
                    "memberId": member_id,
                    "type": "CREDIT_CARD",
                    "cardId": card_id,
                },
                "creditChargeOptions": {
                  "authorizationMode": "AUTH",
                  "useTds2": True,
                  "useFraudDetection": True,
                  "paymentMethod": "ONE_TIME",
                }
              }
            }

        try:
            response = self.client.post("credit/on-file/charge", payload)
            logger.info(f"Successfully created transaction for order: {order_id}")
            return response
        except GMOAPIException as e:
            logger.error(f"Failed to create transaction for order {order_id}: {e!s}")
            raise

    def finalize_3d_secure_payment(self, access_id: str):
        payload = {
            "accessId": access_id,
        }

        try:
            response = self.client.post("tds2/finalizeCharge", payload)
            logger.info(f"Finalize 3ds charge")
            return response
        except GMOAPIException as e:
            logger.error(f"Failed to finalize transaction {e!s}")
            raise

    def update_order(self, access_id: str, amount: str):
        payload = {
            "accessId": access_id,
            "amount": amount,
            "authorizationMode": "CAPTURE",
        }
        try:
            response = self.client.post("order/update", payload)
            logger.info(f"Successfully updated order for access_id: {access_id}")
            return response
        except GMOAPIException as e:
            logger.error(f"Failed to update order for access_id {access_id}: {e!s}")
            raise

    def capture_transaction(self, access_id: str) -> dict[str, Any]:
        """Captures an authorized transaction with a different amount in GMO (AlterTran)."""
        payload = {
            "accessId": access_id,
        }

        try:
            response = self.client.post("order/capture", payload)
            logger.info(f"Successfully captured transaction")
            return response
        except GMOAPIException as e:
            logger.error(f"Failed to capture transaction {e!s}")
            raise

    def cancel_transaction(self, access_id: str) -> dict[str, Any]:
        """Cancels a transaction equivalent in GMO (AlterTran)."""
        payload = {
            "accessId": access_id,
        }

        try:
            response = self.client.post("order/cancel", payload)
            logger.info(f"Successfully cancelled transaction")
            return response
        except GMOAPIException as e:
            logger.error(f"Failed to cancel transaction")
            raise

    def inquiry_transaction_order(self, access_id: str) -> dict[str, Any]:
        """Cancels a transaction equivalent in GMO (AlterTran)."""
        payload = {
            "accessId": access_id,
        }

        try:
            response = self.client.post("order/inquiry", payload)
            return response
        except GMOAPIException as e:
            logger.error(f"Failed to inquiry transaction")
            raise
