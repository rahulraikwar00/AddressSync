
## Badges

Add badges from somewhere like: [shields.io](https://shields.io/)

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)


![Logo](https://i.imgur.com/PQPfHuh.jpg)



# Address Syncing System

**This microservice aims to streamline the process of updating personal information across multiple documents. It uses the Aadhaar number as a base document, and allows users to request updates to be synced to other linked documents of their choice. The syncing system will notify and ask organizations to sync the updates from the Aadhaar document, and the organizations have the option to accept or reject the request with a valid reason for rejection. The user is notified about the status of their request and the updated details are fetched from the Digi locker by the organization. To ensure security, the syncing system is incorporated internally into UIDAI's system.**

**Features**
 User registration: Allows agencies to register for the service by providing their agency name, email, password, and confirm password.
Sending update requests: Allows users to send requests to update their address information, which will be sent to the selected agencies for approval or rejection.
Agency response: Enables agencies to view and respond to update requests, either approving or rejecting the request with a valid reason for rejection.
Data retrieval: Provides functionality for both users and agencies to retrieve data on agencies and update requests.
SMS notifications: Sends SMS notifications to users and agencies regarding the status of update requests.
Secure authentication: Uses OAuth2 and JWT for authentication and authorization.
Internal representation of request status: Uses an internal representation of request status, with a value of 0 for pending, -1 for rejection, and 1 for approval.
FastAPI and Twilio integration: Built using FastAPI and utilizes Twilio as a message service.



|Parameter|	Type|	Description|
|api_key	|string |Required. Your API key.|
|request_id	|string|	Required. The ID of the update request being responded to.|
|response|	string|	Required. The agency's response to the request, either "approve" or "decline".|
|reason	|string	|Optional. A valid reason for declining the request, if applicable.


## License

[MIT](https://choosealicense.com/licenses/mit/)



## API Reference

#### Get all items
Endpoints
Copy code
POST /register
Parameter	Type	Description
agency_name	string	Required. The agency name.
email	string	Required. The agency's email address.
password	string	Required. The agency's password.
confirm_password	string	Required. Confirmation of the agency's password.
Copy code
GET /get_data_of_agencies
Parameter	Type	Description
api_key	string	Required. Your API key.
Copy code
POST /send_update_request
Parameter	Type	Description
api_key	string	Required. Your API key.
customer_id	string	Required. The customer's account number or unique identifier.
agency_id	string	Required. The ID of the agency to which the update request is being sent.
Copy code
GET /get_request
Parameter	Type	Description
api_key	string	Required. Your API key.
Copy code
POST /ag_response
Parameter	Type	Description
api_key	string	Required. Your API key.
request_id	string	Required. The ID of the update request being responded to.
response	string	Required. The agency's response to the request, either "approve" or "decline".
reason	string	Optional. A valid reason for declining the request, if applicable.





Endpoints
/register: Allows agencies to register for the service by providing their agency name, email, password, and confirm password.
/send_update_request: Allows users to send requests to update their address information.
/get_request: Provides functionality for both users and agencies to retrieve data on agencies and update requests.
/ag_response: Enables agencies to view and respond to update requests, either approving or rejecting the request with a valid reason for rejection.
Authentication
The service uses OAuth2 and JWT for authentication and authorization. Users and agencies must obtain and use the required authentication credentials in order to use the API.

Example usage
```python
import requests

# Send an update request
data = {
    "custid": "123456",
    "agencyid": "agency1",
    "add": "new address"
}

response = requests.post("http://localhost:8000/send_update_request", data=data)
print(response.text)

# Get request data
response = requests.get("http://localhost:8000/get_request")
print(response.json())

# Respond to a request
data = {
    "reqid": "123456",
    "agencyid": "agency1",
    "status": "1"
}

response = requests.post("http://localhost:8000/ag_response", data=data)
print(response.text


```



evelopment
To set up a development environment for the API, follow these steps:

Install the required dependencies by running pip install -r requirements.txt.
Set up a local database by running the cr_db() function on startup.
Set the environment variables for the Twilio API key and phone number.
Run the API by executing uvicorn main:app --reload.
License
The API is released under the MIT license. You are free to use, modify, and distribute the API as long as you include the original copyright and license notice in any copies.


## Documentation

[Documentation](https://linktodocumentation)
