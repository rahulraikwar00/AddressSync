
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





 | Parameter |	Type |	Description |

 api_key	string	Required. Your API key.
request_id	string	Required. The ID of the update request.
response	string	Required.


## License

[MIT](https://choosealicense.com/licenses/mit/)


| Parameter | Type | Description |
|-|-|-
| Parameter | Type | Description |
|-|-|-
| Parameter | Type | Description |
|-|-|-

## API Reference

#### Get all items

```http
  GET /api/items
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `api_key` | `string` | **Required**. Your API key |
|           |          |                            |
| :-------- | :------- | :------------------------- |
| `register`| `string` | **Required**. Your API key |

#### Get item

```http
  GET /api/items/${id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. Id of item to fetch |


## Documentation

[Documentation](https://linktodocumentation)


## Used By

This project is used by the following companies:

- Digilocker
- UIDAI


## Tech Stack

**Client:** React, Redux, TailwindCSS, Nextjs

**Server:** python, FastAPI, twilio

