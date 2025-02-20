import logging
from typing import Any, Optional

from ..gmo_client import GMOClient, get_client
from GMOPayment.exceptions import GMOAPIError

logger = logging.getLogger(__name__)

class GMOTransactionService:
    def __init__(self, client: Optional[GMOClient] = None):
        self.client = client or get_client()

    def create_transaction(self, order_id: str, amount: int, job_cd: str = "AUTH") -> dict[str, Any]:
        """Creates a transaction equivalent in GMO (EntryTran)."""
        payload = {
            "ShopID": self.client.config.shop_id,
            "ShopPass": self.client.config.shop_password,
            "OrderID": order_id,
            "JobCd": job_cd,
            "Amount": amount,
        }

        try:
            response = self.client.post("EntryTran.idPass", payload)
            logger.info(f"Successfully created transaction for order: {order_id}")
            return response
        except GMOAPIError as e:
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
        except GMOAPIError as e:
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
        except GMOAPIError as e:
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
        except GMOAPIError as e:
            logger.error(f"Failed to cancel transaction for order {order_id}: {e!s}")
            raise
