from twilio.rest import Client

# Your Account SID from twilio.com/console
# account_sid = "ACd5aaf3fa3e82695e198e605da88f7bab"
# # Your Auth Token from twilio.com/console
# auth_token  = "49c4ab6547494e7a0bf8a0b9c65b7957"

# client = Client(account_sid, auth_token)

# message = client.messages.create(
#     to="+15558675309", 
#     from_="+15017250604",
#     body="Hello from Python!")

# print(message.sid)


from twilio.rest import Client 
 
account_sid = 'ACd5aaf3fa3e82695e198e605da88f7bab' 
auth_token = '49c4ab6547494e7a0bf8a0b9c65b7957' 
client = Client(account_sid, auth_token) 
 
message = client.messages.create(         
                              to='+917223888360' 
                          ) 
 
print(message.sid)