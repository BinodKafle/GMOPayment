import logging
from typing import Any

from ..gmo_client import GMOHttpClient
from GMOPayment.exceptions import GMOAPIException

logger = logging.getLogger(__name__)

class GMOTransactionService:
    def __init__(self):
        self.client = GMOHttpClient()

    def create_transaction_with_payment_method(self, order_id: int, card_token: str) -> dict[str, Any]:
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

    def confirm_transaction(self, access_id: str, access_pass: str, order_id: str, method: int, card_no: str | None = None, expire: str | None = None, security_code: str | None = None) -> dict[str, Any]:
        """Executes a transaction equivalent to confirming a payment (ExecTran)."""
        payload = {
            "AccessID": access_id,
            "AccessPass": access_pass,
            "OrderID": order_id,
            "Method": method,
        }

        if card_no and expire:
            payload["CardNo"] = card_no
            payload["Expire"] = expire
        if security_code:
            payload["SecurityCode"] = security_code

        try:
            response = self.client.post("ExecTran.idPass", payload)
            logger.info(f"Successfully confirmed transaction for order: {order_id}")
            return response
        except GMOAPIException as e:
            logger.error(f"Failed to confirm transaction for order {order_id}: {e!s}")
            raise

    def capture_transaction(self, access_id: str, access_pass: str, order_id: str, amount: int) -> dict[str, Any]:
        """Captures an authorized transaction with a different amount in GMO (AlterTran)."""
        payload = {
            "AccessID": access_id,
            "AccessPass": access_pass,
            "OrderID": order_id,
            "JobCd": "SALES",  # Capture the authorized amount
            "Amount": amount,
        }

        try:
            response = self.client.post("AlterTran.idPass", payload)
            logger.info(f"Successfully captured transaction for order {order_id} with amount: {amount}")
            return response
        except GMOAPIException as e:
            logger.error(f"Failed to capture transaction for order {order_id}: {e!s}")
            raise

    def cancel_transaction(self, access_id: str, access_pass: str, order_id: str, job_cd: str = "VOID") -> dict[str, Any]:
        """Cancels a transaction equivalent in GMO (AlterTran)."""
        payload = {
            "AccessID": access_id,
            "AccessPass": access_pass,
            "OrderID": order_id,
            "JobCd": job_cd,
        }

        try:
            response = self.client.post("AlterTran.idPass", payload)
            logger.info(f"Successfully cancelled transaction for order: {order_id}")
            return response
        except GMOAPIException as e:
            logger.error(f"Failed to cancel transaction for order {order_id}: {e!s}")
            raise
