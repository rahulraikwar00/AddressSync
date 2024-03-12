from pydantic import BaseModel
from twilio.rest import Client
from decouple import config  # You can use python-decouple for managing environment variables

class SMSSchema(BaseModel):
    to: str
    body: str

def send_sms(sms_data: SMSSchema):
    """
    Endpoint to send an SMS using Twilio.
    """
    try:
        # Twilio credentials
        account_sid = config('TWILIO_ACCOUNT_SID')
        auth_token = config('TWILIO_AUTH_TOKEN')
        twilio_phone_number = config('TWILIO_PHONE_NUMBER')

        # Initialize Twilio client
        client = Client(account_sid, auth_token)

        to_number = sms_data.to
        sms_body = sms_data.body

        # Send SMS
        sms = client.messages.create(
            body=sms_body,
            to=to_number,
            from_=twilio_phone_number
        )

        return {"status": "SMS sent successfully", "sid": sms.sid}

    except Exception as e:
        return {"status": "Failed to send SMS", "error": str(e)}

# if __name__ == "__main__":
#     # Example data for testing
#     sms_data = {"to": "+917223888360", "body": "Hello, this is your SMS message!"}

#     # Create an instance of the SMSSchema model
#     sms_model = SMSSchema(**sms_data)

#     # Send SMS
#     result = send_sms(sms_data=sms_model)

class SmsBody:
    
    def pending():
        return """
        Your request is pending approval. Thank you for your patience.
        """
    def approved():
        return """
        Good news! Your request has been approved. 
        Please check your details for accuracy.
        """
    def rejected():
        return """
        We regret to inform you that your request has been rejected. 
        If you have further questions, please contact our support team.
        """

