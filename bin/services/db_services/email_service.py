import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bin.config import settings


class EmailService:
    # @staticmethod
    # def send_otp_mail(email:str, otp_code: str):
    #     try:
    #         # Create message container
    #         msg = MIMEMultipart()
    #         msg['From'] = settings.SMTP_SENDER_MAIL
    #         msg['To'] = email
    #         msg['Subject'] = "Your Account Activation OTP"
    #
    #         # Email body
    #         body = f"""
    #                 <html>
    #                     <body>
    #                         <h2>Account Activation</h2>
    #                         <p>Your OTP for account activation is: <strong>{otp_code}</strong></p>
    #                         <p>This OTP is valid for 15 minutes.</p>
    #                         <p>If you didn't request this, please ignore this email.</p>
    #                     </body>
    #                 </html>
    #                 """
    #
    #         msg.attach(MIMEText(body, 'html'))
    #
    #         # Create SMTP connection
    #         if settings.SMTP_ENCRYPTION == 'ssl':
    #             server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
    #         else:
    #             server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
    #             if settings.SMTP_ENCRYPTION == 'tls':
    #                 server.starttls()
    #
    #         # Login and send email
    #         server.login(settings.SMTP_SENDER_MAIL, settings.SMTP_SENDER_PW)
    #         server.send_message(msg)
    #         server.quit()
    #
    #         return True
    #     except Exception as e:
    #         print(f"Error sending email: {e}")
    #         return False

    @staticmethod
    def send_otp_mail(email: str, otp_code: str):
        try:
            # Create message container
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_SENDER_MAIL
            msg['To'] = email
            msg['Subject'] = "Your Account Activation OTP"

            # Email body
            body = f"""
                     <html>
                         <body>
                             <h2>Account Activation</h2>
                             <p>Your OTP for account activation is: <strong>{otp_code}</strong></p>
                             <p>This OTP is valid for 15 minutes.</p>
                             <p>If you didn't request this, please ignore this email.</p>
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