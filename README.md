
## Badges

Add badges from somewhere like: [shields.io](https://shields.io/)

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)


![Logo](https://i.imgur.com/PQPfHuh.jpg)



# Address Syncing System

This microservice aims to streamline the process of updating personal information across multiple documents. It uses the Aadhaar number as a base document, and allows users to request updates to be synced to other linked documents of their choice. The syncing system will notify and ask organizations to sync the updates from the Aadhaar document, and the organizations have the option to accept or reject the request with a valid reason for rejection. The user is notified about the status of their request and the updated details are fetched from the Digi locker by the organization. To ensure security, the syncing system is incorporated internally into UIDAI's system.

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

