
## Badges

Add badges from somewhere like: [shields.io](https://shields.io/)

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)


![Logo](https://i.imgur.com/PQPfHuh.jpg)


# Adlink

Adlink API is a FastAPI-based RESTful API providing endpoints for registering agencies, updating requests for users, and responding to those requests for agencies. It also includes endpoints for getting data of agencies and requests, and generating access tokens. The API documentation is available through Swagger UI, and it provides detailed descriptions for each endpoint.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:

    ```bash
    git clone <repository-url>
    cd adlink-api
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the FastAPI application:

    ```bash
    uvicorn main:app --reload
    ```

## Usage

Once the application is running, you can access the Swagger UI documentation at `http://127.0.0.1:8000/api/v1/docs` and ReDoc documentation at `http://127.0.0.1:8000/api/v1/redoc` for detailed information on available endpoints and their usage.

## Endpoints

### Register New Agency

- **Endpoint:** `POST /api/v1/register`
- **Description:** Register a new agency.
- **Request Body:**
  - `agency`: An instance of the agency schema.
- **Response:**
  - `"data uploaded"` if successful.
  - `"wrong confirm pass"` if the password and confirm password do not match.

### Send Update Request

- **Endpoint:** `GET /api/v1/send_update_request`
- **Description:** Send an update request for a user's address.
- **Query Parameters:**
  - `name`: Name of the user.
  - `address`: Address of the user.
  - `phone`: Phone number of the user.
  - `agencyid`: ID of the agency.
- **Response:**
  - `"request has been initiated"` if successful.

### Get Update Requests

- **Endpoint:** `GET /api/v1/get_request`
- **Description:** Get all update requests.
- **Response:**
  - List of dictionaries containing request information.

### Respond to Update Request

- **Endpoint:** `GET /api/v1/ag_response`
- **Description:** Respond to a user's update request.
- **Query Parameters:**
  - `reqid`: ID of the request.
  - `status`: Status of the request.
- **Response:**
  - `"response has been sent to the applicant"` if successful.

### Get Data of All Agencies

- **Endpoint:** `GET /api/v1/get_data_of_agencies`
- **Description:** Get data of all agencies.
- **Response:**
  - List of dictionaries containing agency information.

### Get Access Token

- **Endpoint:** `POST /api/v1/token`
- **Description:** Get an access token.
- **Request Body:**
  - `username`: Username of the user.
  - `password`: Password of the user.
- **Response:**
  - JSON object containing `access_token` and `token_type`.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the [MIT License](LICENSE).

