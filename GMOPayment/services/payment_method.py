from typing import Any, Optional
import logging

from ..gmo_client import GMOClient, get_client
from GMOPayment.exceptions import GMOAPIError


logger = logging.getLogger(__name__)


class GMOPaymentMethodService:
    def __init__(self, client: Optional[GMOClient] = None):
        self.client = client or get_client()

    def save_card(self, member_id: str, card_no: str, expire: str, security_code: str | None = None) -> dict[str, Any]:
        """Saves a credit card for a member in the GMO Payment Gateway."""
        payload = {
            "SiteID": self.client.config.site_id,
            "SitePass": self.client.config.site_password,
            "MemberID": member_id,
            "CardNo": card_no,
            "Expire": expire,  # Format: YYMM
        }
        if security_code:
            payload["SecurityCode"] = security_code

        try:
            response = self.client.post("SaveCard.idPass", payload)
            logger.info(f"Successfully saved card for member: {member_id}")
            return response
        except GMOAPIError as e:
            logger.error(f"Failed to save card for member {member_id}: {e!s}")
            raise

    def get_saved_cards(self, member_id: str) -> dict[str, Any]:
        """Retrieves saved cards for a member."""
        payload = {
            "SiteID": self.client.config.site_id,
            "SitePass": self.client.config.site_password,
            "MemberID": member_id,
        }

        try:
            response = self.client.post("SearchCard.idPass", payload)
            logger.info(f"Successfully retrieved cards for member: {member_id}")
            return response
        except GMOAPIError as e:
            logger.error(f"Failed to retrieve cards for member {member_id}: {e!s}")
            raise

    def delete_card(self, member_id: str, card_seq: str) -> dict[str, Any]:
        """Deletes a saved card from the GMO Payment Gateway."""
        payload = {
            "SiteID": self.client.config.site_id,
            "SitePass": self.client.config.site_password,
            "MemberID": member_id,
            "CardSeq": card_seq,
        }

        try:
            response = self.client.post("DeleteCard.idPass", payload)
            logger.info(f"Successfully deleted card {card_seq} for member: {member_id}")
            return response
        except GMOAPIError as e:
            logger.error(f"Failed to delete card {card_seq} for member {member_id}: {e!s}")
            raise

    def process_google_pay(self, order_id: str, token: str) -> dict[str, Any]:
        """Handles Google Pay transactions."""
        payload = {
            "ShopID": self.client.config.shop_id,
            "ShopPass": self.client.config.shop_password,
            "OrderID": order_id,
            "Token": token,
        }

        try:
            response = self.client.post("ExecTranGooglePay.idPass", payload)
            logger.info(f"Successfully processed Google Pay transaction for order: {order_id}")
            return response
        except GMOAPIError as e:
            logger.error(f"Failed to process Google Pay transaction for order {order_id}: {e!s}")
            raise

    def process_apple_pay(self, order_id: str, token: str) -> dict[str, Any]:
        """Handles Apple Pay transactions."""
        payload = {
            "ShopID": self.client.config.shop_id,
            "ShopPass": self.client.config.shop_password,
            "OrderID": order_id,
            "Token": token,
        }

        try:
            response = self.client.post("ExecTranApplePay.idPass", payload)
            logger.info(f"Successfully processed Apple Pay transaction for order: {order_id}")
            return response
        except GMOAPIError as e:
            logger.error(f"Failed to process Apple Pay transaction for order {order_id}: {e!s}")
            raise
