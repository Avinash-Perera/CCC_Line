from email.message import EmailMessage
import os
import smtplib
from bin.response.response_model import ResponseModel,ErrorResponseModel

gmail_user = os.getenv("GMAIL_USER")
gmail_pass = os.getenv("GMAIL_PASS")

outlook_user = os.getenv("OUTLOOK_USER")
outlook_pass = os.getenv("OUTLOOK_PASS")


def send_email(request):
    try:
        msg = EmailMessage()
        msg['Subject'] = request.subject
        msg['From'] = outlook_user
        msg['To'] = gmail_user

        msg.set_content(f"""
            New Message Submitted

            Name: {request.name}
            E-mail: {request.email}
            
            message: {request.msg}
            """)

        # Send email using Gmail
        with smtplib.SMTP_SSL('mail.ambrumsolutions.com', 465) as smtp:
            smtp.login(outlook_user, outlook_pass)
            smtp.send_message(msg)

        # === Reply to Applicant ===
        confirmation = EmailMessage()
        confirmation['Subject'] = f"Your message is submitted - CCC Line"
        confirmation['From'] = outlook_user
        confirmation['To'] = request.email

        confirmation.set_content(f"""
            Dear {request.name},

            Thank you for your message.

            We have forwarded your message to ccc-lines, we will contact you later for further information

            Best regards,  
            Team  
            CCC Lines
            """)

        with smtplib.SMTP_SSL('mail.ambrumsolutions.com', 465) as smtp:
            smtp.login(outlook_user, outlook_pass)
            smtp.send_message(confirmation)


        return " email sent "

    except Exception as e:
        return ErrorResponseModel(str(e), 400)