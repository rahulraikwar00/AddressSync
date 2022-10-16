
## Badges

Add badges from somewhere like: [shields.io](https://shields.io/)

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)


![Logo](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/th5xamgrr6se0x5ro4g6.png)


# Address Syncing System

Users willing to update even a tiny piece of information in one document face issues in changing the same in other documents as all the processes have to be carried out manually by the users.
The microservice uses Aadhaar as the base document for various other documents that are linked to the Aadhaar number to carry forward address updates done in Aadhaar to other documents as per the user’s choice. The syncing system will notify and ask the selected organizations to sync the user updates from Aadhaar only when requested by the user. The organization has the choice to accept or reject the update request. The organization is liable to provide a valid reason for the rejection of the request. 
User is notified about the status of his request. Internal representation of status:  
On initiation/pending : status =0 
On rejection : status =-1
On approved : status = 1
The updated details of the user are fetched from Digi locker by the organization. The organization then makes changes to its user data as per the changes made in Aadhaar. UIDAI will send a notification to the user as well, informing him about the status of request. After carrying out necessary changes organization will send an acknowledgment message to the user to ensure him about the updates.
To maintain security in the complete environment, the syncing system has to be incorporated internally into UIDAI’s system.

## License

[MIT](https://choosealicense.com/licenses/mit/)


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

