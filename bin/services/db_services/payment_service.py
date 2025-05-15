import base64
import uuid
from typing import Dict, Any

import httpx
from fastapi import HTTPException

from bin.config import MERCHANT_CREDENTIALS, MPGS_API_VERSION, MPGS_BASE_URL
from bin.helpers.http_request_logger import HttpRequestLogger
from bin.utils.response_codes import PaymentStatus, PaymentResponseCode, get_error_message


class PaymentService:

    @staticmethod
    async def create_payment_session(donation, return_url: str, currency: str, db):
        credentials = MERCHANT_CREDENTIALS.get(currency)
        if not credentials:
            raise HTTPException(status_code=400, detail=f"Unsupported currency: {currency}")

        auth_string = f"{credentials['api_username']}:{credentials['api_password']}"
        auth_token = base64.b64encode(auth_string.encode()).decode()

        order_id = str(uuid.uuid4())

        api_path = f"/version/{MPGS_API_VERSION}/merchant/{credentials['merchant_id']}/session"
        payload = {
            "apiOperation": "INITIATE_CHECKOUT",
            "interaction": {
                "merchant": {
                    "name": "CCC Foundation"
                },
                "operation": "PURCHASE",
                "displayControl": {
                    "billingAddress": "HIDE",
                    "customerEmail": "HIDE",
                    "shipping": "HIDE"
                },
                "returnUrl": return_url
            },
            "order": {
                "id": order_id,
                "currency": currency,
                "description": donation.message or "Donation to CCC Foundation",
                "amount": f"{donation.amount:.2f}"
            }
        }

        logger = HttpRequestLogger(base_url=MPGS_BASE_URL, db=db)
        logger.set_api(api_path).set_payload(payload).add_header("Authorization", f"Basic {auth_token}").add_header(
            "Content-Type", "application/json")

        try:
            response = await logger.post()
            print("Create Payment Session Response:", response.text)
            response.raise_for_status()
            data = response.json()
            return {
                "session_id": data['session']['id'],
                "success_indicator": data['successIndicator'],
                "order_id": order_id
            }
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=400, detail=f"Payment gateway error: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def verify_payment(order_id: str, currency: str, db) -> Dict[str, Any]:
        credentials = MERCHANT_CREDENTIALS.get(currency)
        if not credentials:
            raise HTTPException(status_code=400, detail=f"Unsupported currency: {currency}")

        auth_string = f"{credentials['api_username']}:{credentials['api_password']}"
        auth_token = base64.b64encode(auth_string.encode()).decode()

        api_path = f"/version/{MPGS_API_VERSION}/merchant/{credentials['merchant_id']}/order/{order_id}"

        logger = HttpRequestLogger(base_url=MPGS_BASE_URL, db=db)
        logger.set_api(api_path).add_header("Authorization", f"Basic {auth_token}")

        try:
            response = await logger.get()
            response.raise_for_status()
            data = response.json()

            result = data.get("result", "")
            transactions = data.get("transaction", [])

            gateway_code = (
                transactions[0].get("response", {}).get("gatewayCode", "")
                if transactions
                else data.get("response", {}).get("gatewayCode", "")
            )

            if not gateway_code:
                raise ValueError("No gateway code found in response")

            # Convert to enum
            try:
                payment_response_code = PaymentResponseCode(gateway_code)
            except ValueError:
                payment_response_code = "An Error Occurred"

            # Check all transactions for approval (if they exist)
            all_approved = all(
                tx.get("response", {}).get("gatewayCode") == "APPROVED"
                for tx in transactions
            ) if transactions else True

            is_success = (
                    result == "SUCCESS"
                    and payment_response_code == PaymentResponseCode.APPROVED
                    and all_approved
            )

            return {
                "status": PaymentStatus.COMPLETED if is_success else PaymentStatus.FAILED,
                "gateway_code": payment_response_code,
                "raw_response": data,
                "decline_reason": None if is_success else get_error_message(payment_response_code)
            }

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=400, detail=f"Payment verification error: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))





