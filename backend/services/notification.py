# services/notification.py
from twilio.rest import Client
from core.config import settings
from core.logging import ActivityLogger
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.client = None
        self.enabled = settings.ENABLE_SMS_NOTIFICATIONS

        if self.enabled and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                self.client = Client(
                    settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                logger.info("Twilio client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.enabled = False
        else:
            logger.warning(
                "Twilio notifications are disabled or not configured")

    def send_sms(self, to_phone: str, message: str) -> bool:
        """Send SMS notification"""
        if not self.enabled or not self.client:
            logger.info(f"SMS would be sent to {to_phone}: {message}")
            return False

        try:
            # Format phone number (ensure it has country code)
            if not to_phone.startswith('+'):
                # Default to India country code if not provided
                to_phone = '+91' + to_phone.lstrip('0')

            message = self.client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_phone
            )

            logger.info(f"SMS sent to {to_phone}: SID {message.sid}")
            ActivityLogger.log_notification(to_phone, "SMS", message.sid)
            return True

        except Exception as e:
            logger.error(f"Failed to send SMS to {to_phone}: {e}")
            return False

    def send_whatsapp(self, to_phone: str, message: str) -> bool:
        """Send WhatsApp notification"""
        if not self.enabled or not self.client or not settings.TWILIO_WHATSAPP_NUMBER:
            logger.info(f"WhatsApp would be sent to {to_phone}: {message}")
            return False

        try:
            # Format phone number
            if not to_phone.startswith('+'):
                to_phone = '+91' + to_phone.lstrip('0')

            message = self.client.messages.create(
                body=message,
                from_=f'whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}',
                to=f'whatsapp:{to_phone}'
            )

            logger.info(f"WhatsApp sent to {to_phone}: SID {message.sid}")
            return True

        except Exception as e:
            logger.error(f"Failed to send WhatsApp to {to_phone}: {e}")
            return False

    def send_request_created(self, user_phone: str, request_id: str, agency_name: str):
        """Send notification when request is created"""
        message = f"""🏠 Address Change Request Created!
        
Request ID: {request_id}
Agency: {agency_name}
Status: Pending

We'll notify you once the agency reviews your request."""

        self.send_sms(user_phone, message)
        self.send_whatsapp(user_phone, message)

    def send_request_approved(self, user_phone: str, request_id: str, agency_name: str, new_address: str):
        """Send notification when request is approved"""
        message = f"""✅ Address Change Request Approved!

Request ID: {request_id}
Agency: {agency_name}
New Address: {new_address}

Your address has been successfully updated in our system."""

        self.send_sms(user_phone, message)
        self.send_whatsapp(user_phone, message)

    def send_request_rejected(self, user_phone: str, request_id: str, agency_name: str, reason: str = None):
        """Send notification when request is rejected"""
        message = f"""❌ Address Change Request Rejected!

Request ID: {request_id}
Agency: {agency_name}
"""
        if reason:
            message += f"Reason: {reason}\n\n"
        message += "Please submit a new request with correct details."

        self.send_sms(user_phone, message)
        self.send_whatsapp(user_phone, message)

    def send_request_cancelled(self, user_phone: str, request_id: str):
        """Send notification when request is cancelled"""
        message = f"""🔄 Address Change Request Cancelled!

Request ID: {request_id}
You have successfully cancelled this request."""

        self.send_sms(user_phone, message)
        self.send_whatsapp(user_phone, message)

    def send_otp(self, user_phone: str, otp: str):
        """Send OTP for verification"""
        message = f"""🔐 Your Address Sync Verification Code

OTP: {otp}
Valid for 10 minutes.

Do not share this code with anyone."""

        self.send_sms(user_phone, message)
        self.send_whatsapp(user_phone, message)


# Create singleton instance
notification_service = NotificationService()
