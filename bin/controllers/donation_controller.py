import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import quote

from fastapi import HTTPException
from requests import Session
from sqlalchemy import select
from starlette.responses import HTMLResponse, FileResponse, RedirectResponse

from bin.db.postgresDB import db_connection
from bin.models import pg_models
from bin.models.pg_models import DonationTable
from bin.response.response_model import ResponseModel,ErrorResponseModel
from bin.services.db_services.donation_service import create_new_donation_record, currency_list, donation_list, \
    sum_of_donations, payment_callback_function, get_currency_by_id
from bin.services.db_services.payment_service import PaymentService
from bin.config import RETURN_URL, APP_URL, settings
from bin.utils.response_codes import PaymentStatus, PaymentResponseCode, is_retryable_error, get_error_message


class DonationManager():
    def __init__(self, db: Session = None):
        self.db = db if db else next(db_connection())
        self.payment_service = PaymentService()

    async def _send_confirmation_email(self, donation: DonationTable):
        """Send payment confirmation email to donor"""
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_SENDER_MAIL
            msg['To'] = donation.email
            msg['Subject'] = "Thank you for your donation!"

            # Email body
            body = f"""
               <html>
                   <body>
                       <h2>Thank you for your generous donation!</h2>
                       <p>Dear {donation.first_name} {donation.second_name},</p>
                       <p>We have successfully received your donation of {donation.amount} {get_currency_by_id(donation.currency_id)}.</p>
                       <p>Your support means the world to us.</p>
                       <p>With gratitude,<br/>CCC Foundation Team</p>
                   </body>
               </html>
               """
            msg.attach(MIMEText(body, 'html'))

            # Send email
            with smtplib.SMTP_SSL(
                    host=settings.SMTP_HOST,
                    port=settings.SMTP_PORT
            ) as server:
                server.login(settings.SMTP_SENDER_MAIL, settings.SMTP_SENDER_PW)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Failed to send confirmation email: {str(e)}")
            return False

    async def donation(self, request):
        try:
            donation = None
            try:
                donation = create_new_donation_record(request, self.db)
                self.db.flush()

                currency = get_currency_by_id(donation.currency_id)

                currency_code = currency.currency_code

                return_url = f"{RETURN_URL}"
                payment_result = await self.payment_service.create_payment_session(
                    donation=donation,
                    return_url=return_url,
                    currency=currency_code,
                    db=self.db
                )

                transaction = pg_models.Transaction(
                    donation_id=donation.record_id,
                    mpgs_order_id=payment_result["order_id"],
                    session_id=payment_result["session_id"],
                    success_indicator=payment_result["success_indicator"],
                    amount=donation.amount,
                    currency=currency_code,
                    status="initiated"
                )
                self.db.add(transaction)
                self.db.commit()

                return ResponseModel({
                    "donation_id": donation.record_id,
                    "payment_url": f"{APP_URL}/payment-page/{donation.record_id}",
                }, "Donation created successfully")

            except Exception as e:
                self.db.rollback()
                if donation and donation.record_id:
                    self.db.delete(donation)
                    self.db.commit()
                raise e

        except HTTPException as e:
            return ErrorResponseModel(e.detail, e.status_code)
        except Exception as e:
            return ErrorResponseModel(str(e), 400)

    async def payment_page(self, donation_id: int):
        transaction =  self.db.execute(
            select(pg_models.Transaction)
            .where(pg_models.Transaction.donation_id == donation_id)
            .order_by(pg_models.Transaction.created_at.desc())
        )
        transaction = transaction.scalar_one_or_none()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Redirecting to Payment</title>
                <script 
                    src="https://cbcmpgs.gateway.mastercard.com/static/checkout/checkout.min.js"
                    data-error="errorCallback" 
                    data-cancel="cancelCallback">
                </script>
                <script type="text/javascript">
                    function errorCallback(error) {{
                        console.error("Payment Error:", JSON.stringify(error));
                    }}

                    function cancelCallback() {{
                        console.warn('Payment was cancelled.');
                    }}

                    window.onload = function() {{
                        Checkout.configure({{
                            session: {{
                                id: '{transaction.session_id}'
                            }}
                        }});
                        Checkout.showPaymentPage();
                    }};
                </script>
            </head>
            <body>
                <p>Redirecting to payment page... Please wait.</p>
            </body>
            </html>
            """
        return HTMLResponse(content=html_content)

    async def payment_callback(self, request):
        try:
            payment_result = await payment_callback_function(request, self.db)

            if payment_result["status"] == PaymentStatus.COMPLETED:
                # Get the donation record
                donation = self.db.execute(
                    select(pg_models.DonationTable)
                    .where(pg_models.DonationTable.record_id == payment_result["transaction"].donation_id)
                ).scalar_one_or_none()

                if donation:
                    # Send confirmation email (fire and forget)
                    await self._send_confirmation_email(donation)

                return await self.payment_success_page(payment_result["transaction"].donation_id)
            else:
                gateway_code = payment_result.get("gateway_code")
                return await self.handle_payment_failure(
                    payment_result["transaction"].donation_id,
                    gateway_code
                )

        except HTTPException as e:
            return await self.payment_failure_page(None, str(e.detail))
        except Exception as e:
            return await self.payment_failure_page(None,  str(e))

    async def handle_payment_failure(self, donation_id: int | None, gateway_code: PaymentResponseCode):
        """Handle different failure scenarios with appropriate responses"""
        if is_retryable_error(gateway_code):
            # Could implement auto-retry logic here
            error_msg = f"{get_error_message(gateway_code)}. Please try again."
        else:
            error_msg = get_error_message(gateway_code)

        return await self.payment_failure_page(donation_id, error_msg)

    def get_currency_list(self):
        try:
            currency = currency_list()
            return ResponseModel(currency,'All currency list')
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return ErrorResponseModel(str(e), 400)

    def donation_types(self):
        try:
            donations = donation_list()
            return ResponseModel(donations, 'All donation types')
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return ErrorResponseModel(str(e), 400)

    def get_total_donations(self):
        try:
            total_donation = sum_of_donations()

            return ResponseModel(total_donation,'sum of general donations')

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return ErrorResponseModel(str(e), 400)

    async def payment_success_page(self, donation_id: int | None):
        # You might want to pass donation details later
        return RedirectResponse(
            url=f"/public/html/payment_success_page.html",
            status_code=303
        )

    async def payment_failure_page(self, donation_id: int | None, error_msg: str = None):
        # Encode error message for URL safety
        error_param = quote(error_msg) if error_msg else ""

        return RedirectResponse(
            url=f"/public/html/payment_failure_page.html?error={error_param}",
            status_code=303
        )


donationManager = DonationManager()