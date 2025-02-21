from typing import Any, Optional
import logging

from ..gmo_client import GMOClient, get_client
from GMOPayment.exceptions import GMOAPIError


logger = logging.getLogger(__name__)


class GMOMemberService:
    def __init__(self, client: Optional[GMOClient] = None):
        self.client = client or get_client()

    def create_member(self, member_id: str, member_name: str | None = None) -> dict[str, Any]:
        """Creates a member in the GMO Payment Gateway."""
        payload = {
            "memberId": f"MER-{member_id}",
        }
        if member_name:
            payload["memberName"] = member_name

        try:
            response = self.client.post("member/create", payload)
            logger.info(f"Successfully created member: {member_id}")
            return response
        except GMOAPIError as e:
            logger.error(f"Failed to create member {member_id}: {e!s}")
            raise

    def get_member(self, member_id: str) -> dict[str, Any]:
        """Retrieves a member from the GMO Payment Gateway."""
        payload = {
            "memberId": member_id,
        }

        try:
            response = self.client.post("member/inquiry", payload)
            logger.info(f"Successfully retrieved member: {member_id}")
            return response
        except GMOAPIError as e:
            logger.error(f"Failed to retrieve member {member_id}: {e!s}")
            raise

    def delete_member(self, member_id: str) -> dict[str, Any]:
        """Deletes a member from the GMO Payment Gateway."""
        payload = {
            "SiteID": self.client.config.site_id,
            "SitePass": self.client.config.site_password,
            "MemberID": member_id,
        }

        try:
            response = self.client.post("DeleteMember.idPass", payload)
            logger.info(f"Successfully deleted member: {member_id}")
            return response
        except GMOAPIError as e:
            logger.error(f"Failed to delete member {member_id}: {e!s}")
            raise
