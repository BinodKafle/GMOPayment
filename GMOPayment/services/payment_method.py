import base64
import json
from typing import Any
import logging
from decouple import config
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from ..gmo_client import GMOHttpClient
from GMOPayment.exceptions import GMOAPIException


logger = logging.getLogger(__name__)


class GMOPaymentMethodService:
    def __init__(self):
        self.client = GMOHttpClient()

    @staticmethod
    def encrypt_card(card_no: str, card_holder_name: str, expire_month: str, expire_year: str, security_code: str | None = None) -> str:
        # Public key string from the management screen (Base64 encoded)
        public_key_string = config("PM_TOKEN_PUBLIC_KEY")

        # Card information JSON string
        card_info_json = json.dumps({
            "card": {
                "cardNumber": card_no,
                "cardholderName": card_holder_name,
                "expiryMonth": expire_month,
                "expiryYear": expire_year,
                "securityCode": security_code
            }
        })

        # Decode the Base64 encoded public key
        decoded_public_key = base64.b64decode(public_key_string)

        # Load the public key
        public_key = serialization.load_der_public_key(decoded_public_key, backend=default_backend())

        # Encrypt the card information
        encrypted_bytes = public_key.encrypt(
            card_info_json.encode(),
            padding.PKCS1v15()
        )

        # Encode the encrypted data in Base64
        encrypted_data = base64.b64encode(encrypted_bytes).decode()

        return encrypted_data

    def create_token(self, card_no: str, card_holder_name: str, expire_month: str, expire_year: str, security_code: str | None = None) -> dict[str, Any]:
        """Creates a token for a credit card in the GMO Payment Gateway."""
        card_encrypted_data = self.encrypt_card(card_no, card_holder_name, expire_month, expire_year, security_code)
        payload = {
            "encryptionParameters": {
                "type": "UNIQUE_PK",
                "apiKey": config("PM_TOKEN_API_KEY"),
            },
            "encryptedData": card_encrypted_data,
            "createCount": "1"
        }

        try:
            response = self.client.post("payment/CreateToken.json", payload, "pm_token")
            logger.info(f"Successfully created token for card: {card_no}")
            return response
        except GMOAPIException as e:
            logger.error(f"Failed to create token for card {card_no}: {e!s}")
            raise

    def verify_card(self, member_id: str, card_token: str) -> dict[str, Any]:
        payload = {
              "merchant": {
                "name": "Merchant Binod",
                "nameKana": "ジーエムオーストア",
                "nameAlphabet": "Soudan",
                "nameShort": "サンプル",
                "contactName": "Binod Kafle",
                "contactPhone": "0120-123-456",
                "contactOpeningHours": "10:00-18:00",
                "callbackUrl": "https://example.com/callback"
            },
              "order": {
                "orderId": "order-001",
                "transactionType": "CIT",
              },
              "payer": {
                "name": "Saurav Adhikari",
              },
              "creditVerificationInformation": {
                "tokenizedCard": {
                  "type": "MP_TOKEN",
                  "token": card_token
                },
              "creditVerificationOptions": {
                  "useTds2": False,
                  "itemCode": "0000990"
              },
              },
            }
        try:
            response = self.client.post("credit/verifyCard", payload)
            return response
        except GMOAPIException as e:
            logger.error(f"Failed to verify card for token {card_token}: {e!s}")
            raise

    def save_card(self, member_id: str, card_token: str) -> dict[str, Any]:
        """Saves a credit card for a member in the GMO Payment Gateway."""
        payload = {
            "merchant": {
                "name": "Merchant Binod",
                "nameKana": "ジーエムオーストア",
                "nameAlphabet": "Soudan",
                "nameShort": "サンプル",
                "contactName": "Binod Kafle",
                "contactPhone": "0120-123-456",
                "contactOpeningHours": "10:00-18:00",
                "callbackUrl": "https://example.com/callback"
            },
            "creditStoringInformation": {
                "tokenizedCard": {
                    "type": "MP_TOKEN",
                    "token": card_token,
                },
                "onfileCardOptions": {
                    "memberId": member_id,
                },
            },
        }

        try:
            response = self.client.post("credit/storeCard", payload)
            logger.info(f"Successfully saved card for member: {member_id}")
            return response
        except GMOAPIException as e:
            logger.error(f"Failed to save card for member {member_id}: {e!s}")
            raise

    def get_card_details(self, token: str) -> dict[str, Any]:
        """Retrieves saved cards for a member."""
        payload = {
              "cardInformation": {
                "tokenizedCard": {
                  "type": "MP_TOKEN",
                  "token": token
                }
              },
              "additionalOptions": {}
        }

        try:
            response = self.client.post("credit/getCardDetails", payload)
            logger.info(f"Successfully retrieved cards for token: {token}")
            return response
        except GMOAPIException as e:
            logger.error(f"Failed to retrieve cards for token {token}: {e!s}")
            raise

    def delete_card(self, member_id: str, card_seq: str) -> dict[str, Any]:
        """Deletes a saved card from the GMO Payment Gateway."""
        payload = {
            "SiteID": self.client.credentials.site_id,
            "SitePass": self.client.credentials.site_password,
            "MemberID": member_id,
            "CardSeq": card_seq,
        }

        try:
            response = self.client.post("DeleteCard.idPass", payload)
            logger.info(f"Successfully deleted card {card_seq} for member: {member_id}")
            return response
        except GMOAPIException as e:
            logger.error(f"Failed to delete card {card_seq} for member {member_id}: {e!s}")
            raise

    def process_google_pay(self, order_id: str, token: str) -> dict[str, Any]:
        """Handles Google Pay transactions."""
        payload = {
            "ShopID": self.client.credentials.shop_id,
            "ShopPass": self.client.credentials.shop_password,
            "OrderID": order_id,
            "Token": token,
        }

        try:
            response = self.client.post("ExecTranGooglePay.idPass", payload)
            logger.info(f"Successfully processed Google Pay transaction for order: {order_id}")
            return response
        except GMOAPIException as e:
            logger.error(f"Failed to process Google Pay transaction for order {order_id}: {e!s}")
            raise

    def process_apple_pay(self, order_id: str, token: str) -> dict[str, Any]:
        """Handles Apple Pay transactions."""
        payload = {
            "ShopID": self.client.credentials.shop_id,
            "ShopPass": self.client.credentials.shop_password,
            "OrderID": order_id,
            "Token": token,
        }

        try:
            response = self.client.post("ExecTranApplePay.idPass", payload)
            logger.info(f"Successfully processed Apple Pay transaction for order: {order_id}")
            return response
        except GMOAPIException as e:
            logger.error(f"Failed to process Apple Pay transaction for order {order_id}: {e!s}")
            raise
