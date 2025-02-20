from typing import Any, Optional
import logging

from ..gmo_client import GMOClient, get_client
from GMOPayment.exceptions import GMOAPIError


logger = logging.getLogger(__name__)


class GMOMerchantService:
    def __init__(self, client: Optional[GMOClient] = None):
        self.client = client or get_client()
        self.site_id = self.client.config.site_id  # Use separate SiteID for merchants
        self.site_pass = self.client.config.site_id

    def create_merchant_account(self, merchant_id: str, merchant_name: str | None = None) -> dict[str, Any]:
        """Creates a merchant account in GMO (Managed as a special member)."""
        payload = {
            "SiteID": self.site_id,
            "SitePass": self.site_pass,
            "MemberID": f"MER-{merchant_id}",  # Prefix to distinguish merchants
        }
        if merchant_name:
            payload["MemberName"] = merchant_name

        try:
            response = self.client.post("SaveMember.idPass", payload)
            logger.info(f"Successfully created merchant account: {merchant_id}")
            return response
        except GMOAPIError as e:
            logger.error(f"Failed to create merchant account {merchant_id}: {e!s}")
            raise

    def get_merchant_account(self, merchant_id: str) -> dict[str, Any]:
        """Retrieves merchant account details from GMO."""
        payload = {
            "SiteID": self.site_id,
            "SitePass": self.site_pass,
            "MemberID": f"MER-{merchant_id}",
        }

        try:
            response = self.client.post("SearchMember.idPass", payload)
            logger.info(f"Successfully retrieved merchant account: {merchant_id}")
            return response
        except GMOAPIError as e:
            logger.error(f"Failed to retrieve merchant account {merchant_id}: {e!s}")
            raise

    def delete_merchant_account(self, merchant_id: str) -> dict[str, Any]:
        """Deletes a merchant account from GMO."""
        payload = {
            "SiteID": self.site_id,
            "SitePass": self.site_pass,
            "MemberID": f"MER-{merchant_id}",
        }

        try:
            response = self.client.post("DeleteMember.idPass", payload)
            logger.info(f"Successfully deleted merchant account: {merchant_id}")
            return response
        except GMOAPIError as e:
            logger.error(f"Failed to delete merchant account {merchant_id}: {e!s}")
            raise

    def process_payout(self, merchant_id: str, amount: int, bank_details: dict[str, Any]) -> dict[str, Any]:
        """Handles manual payouts for merchants (must integrate external banking API)."""
        logger.info(f"Processing payout of {amount} to merchant: {merchant_id} with bank details: {bank_details}")
        # Since GMO does not support direct payouts, you must integrate a banking API
        return {"status": "success", "message": "Payout initiated manually."}

    def save_merchant_bank_details(self, merchant_id: str, bank_details: dict[str, Any]) -> dict[str, Any]:
        """Saves merchant's bank details for payouts (Handled externally)."""
        # This would typically be stored in your database
        logger.info(f"Saving bank details for merchant {merchant_id}: {bank_details}")
        return {"status": "success", "message": "Bank details saved."}
