from twilio.rest import Client

# class for sending sms using twilio
class sms:
    def __init__(self, message):
        self.message = message



    def send(self):
        # Your Account SID from twilio.com/console
        account_sid = "ACee93b868da4090c888beb2a4284c4e11"
        auth_token = "c05e49060b477ff4d6e5bdf293b2a72f"

        client = Client(account_sid, auth_token)

        message = client.messages.create(
            messaging_service_sid="MG40cd15c171dd86dd36df08f19410290c",
            body=self.message,
            to="+919340334395",
        )
        
        return message.sid

# funcion to send message 
def send_sms(message):
    sms(message).send()