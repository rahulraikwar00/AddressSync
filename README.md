
## Badges

Add badges from somewhere like: [shields.io](https://shields.io/)

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)


![Logo](https://i.imgur.com/PQPfHuh.jpg)

# Aadhaar Information Syncing System

Welcome to the Aadhaar Information Syncing System, a microservice designed to simplify the process of updating personal information across multiple documents. This system utilizes the Aadhaar number as the primary document, allowing users to request updates that will be synchronized with other linked documents of their choosing. The project consists of two main parts: the client-side and the server-side (addressSync).

## Client-Side

The client-side of the project is built using SvelteKit and features a landing page that serves as the main interface for users to interact with the system.

## Server-Side (addressSync)

The server-side, contained within the `addressSync` folder, is the main project that will be used by running basic Docker commands. Users can build the container, set the necessary variables, and run the project using Docker Compose.

## Key Features

1. **User Registration**: Agencies can seamlessly register for the service by providing essential details such as agency name, email, password, and confirmation.

2. **Update Requests**: Users have the ability to submit requests to update their address information. These requests are then sent to selected agencies for approval or rejection.

3. **Agency Responses**: Agencies can conveniently view and respond to update requests, either approving or rejecting them along with a valid reason for rejection.

4. **Data Retrieval**: The system offers functionality for both users and agencies to retrieve information on registered agencies and update requests.

5. **SMS Notifications** (Upcoming): Stay informed with SMS notifications that keep users and agencies in the loop regarding the status of their update requests.

6. **Secure Authentication** (Upcoming): Our system prioritizes security by implementing OAuth2 and JWT for robust authentication and authorization.

7. **Internal Request Status Representation**: Utilizes an internal representation of request status, with `active` indicating a pending status, `reject` for rejection, and `accept` for approval.

8. **FastAPI and Twilio Integration**: Leveraging the power of FastAPI for seamless API development and Twilio for efficient messaging services.

Feel free to explore the functionalities and experience the efficiency of our Aadhaar Information Syncing System.

## Table of Contents
- [Aadhaar Information Syncing System](#aadhaar-information-syncing-system)
  - [Client-Side](#client-side)
  - [Server-Side (addressSync)](#server-side-addresssync)
  - [Key Features](#key-features)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Endpoints](#endpoints)
  - [Data Models](#data-models)
  - [Configuration](#configuration)
  - [Contributing](#contributing)
  - [License](#license)

## Installation

### Client-Side

1. Navigate to the client-side directory:

   ```bash
   cd path/to/client-side
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the development server:

   ```bash
   npm run dev
   ```

### Server-Side (addressSync)

1. Navigate to the `addressSync` directory:

   ```bash
   cd path/to/addressSync
   ```

2. Build the Docker image:

   ```bash
   docker compose up --build
   ```

3. Set environment variables:

   ```bash
   export DATABASE_URL=your_database_url
   export SECRET_KEY=your_secret_key
   export TWILIO_ACCOUNT_SID=your_twilio_account_sid
   export TWILIO_AUTH_TOKEN=your_twilio_auth_token
   export TWILIO_PHONE_NUMBER=your_twilio_phone_number
   ```

4. Run the Docker container using Docker Compose:

   ```bash
   docker-compose up
   ```

## Usage

(Provide instructions for using both the client-side and server-side of the project, including how to run the landing page and the addressSync system using Docker Compose.)

## Endpoints

Describe the available API endpoints and their functionalities.

- `GET /`: Brief description.
- `POST /users/`: Create a new user.
- `POST /agencies/`: Create a new agency.
- ...

## Data Models

Explain the data models used in your application.

- `User`: Description of the User model.
- `Agency`: Description of the Agency model.
- `ActiveRequest`: Description of the ActiveRequest model.

## Configuration

Explain any configuration settings or environment variables that need to be set.

- `DATABASE_URL`: Database connection URL.
- ...


## Contributing

Explain how others can contribute to your project. Include guidelines for submitting issues, feature requests, and pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)

[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)

I have updated the installation instructions for the server-side (addressSync) part of the project to include the use of Docker Compose. However, you will still need to provide specific usage instructions for both parts of the project.
