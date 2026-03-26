# Address Sync System

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://docker.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://sqlalchemy.org)

![Address Sync System](https://i.imgur.com/PQPfHuh.jpg)

---

## 📋 Overview

The **Address Sync System** is a microservice that simplifies updating address information across multiple agencies using Aadhaar as a unique identifier.

Users can request updates → agencies approve/reject → system syncs changes.

---

## ✨ Features

### 🏠 Requester (Citizen)

* Register/Login via Aadhaar
* View agencies
* Submit address update requests
* Track request status
* Cancel pending requests

### 🏢 Agency

* Register/Login
* View pending requests
* Approve/Reject requests
* Access request history

### 📊 Admin

* Status tracking (Pending / Approved / Rejected / Cancelled)
* Filtering
* Stats dashboard
* Audit logs

---

## 🏗️ Tech Stack

### Backend

* FastAPI
* SQLAlchemy
* SQLite / PostgreSQL
* JWT Auth
* Python 3.10+

### Frontend

* HTML, CSS, Vanilla JS

### DevOps

* Docker
* Docker Compose
* Git

---

## ⚙️ System Flow

```
Citizen → Request → Agency
   ↓           ↑
Status ← Approval
   ↓
Address Updated
```

---

## 📦 Prerequisites

* Python 3.10+
* Docker & Docker Compose
* Git
* curl

---

## 🚀 Installation

### 1. Clone

```bash
git clone https://github.com/yourusername/address-sync-system.git
cd address-sync-system
```

---

### 2. Backend Setup

#### Option A: Docker

```bash
cd backend
docker-compose up -d --build
docker-compose logs -f
docker-compose down
```

---

#### Option B: Local

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt

mkdir data static
```

Create `.env`:

```env
DATABASE_URL=sqlite:///./data/address_sync.db
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

Run:

```bash
uvicorn main:app --reload
```

---

## 🌐 Access

| Service | URL                         |
| ------- | --------------------------- |
| App     | http://localhost:8000       |
| Docs    | http://localhost:8000/docs  |
| ReDoc   | http://localhost:8000/redoc |

---

## 💻 Usage

### Demo Users

| Aadhaar      | Name         | Password    |
| ------------ | ------------ | ----------- |
| 123456789012 | Rajesh Kumar | Rajesh@1234 |

### Demo Agencies

| ID                  | Name         |
| ------------------- | ------------ |
| municipal_bangalore | Bangalore MC |

---

## 🔌 API Example

```bash
# Health
curl http://localhost:8000/health

# Register
curl -X POST http://localhost:8000/users/register \
-H "Content-Type: application/json" \
-d '{"aadhaar_number":"123456789012","password":"Test@123"}'
```

---

## 📡 API Endpoints

### User

* POST `/users/register`
* POST `/users/login`
* GET `/users/me`

### Agency

* POST `/agencies/register`
* POST `/agencies/login`

### Requests

* POST `/requests/create`
* GET `/requests/my-requests`
* PUT `/requests/{id}`

---

## 📊 Data Models

### User

```json
{
  "aadhaar_number": "string",
  "name": "string",
  "email": "string",
  "current_address": "string"
}
```

### Request

```json
{
  "id": "uuid",
  "status": "pending | approved | rejected"
}
```

---

## ⚙️ Environment Variables

```env
DATABASE_URL=sqlite:///./data/address_sync.db
SECRET_KEY=secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

## 🐳 Docker

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
```

---

## 🧪 Testing

```bash
python test_full_api.py
```

---

## 🚢 Deployment

### Railway

```bash
railway up
```

### Render

* Build: `pip install -r requirements.txt`
* Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## 🔧 Troubleshooting

### Port Issue

```bash
lsof -i :8000
kill -9 PID
```

### Docker Issue

```bash
sudo systemctl start docker
```

---

## 🤝 Contributing

```bash
git checkout -b feature/new-feature
git commit -m "Add feature"
git push origin feature/new-feature
```

---

## 📄 License

MIT License

---

## 🙌 Credits

* FastAPI
* SQLAlchemy
* Docker

---

## 📞 Contact

* GitHub Issues
* Docs
* Community

---

<div align="center">
Made with ❤️  
</div>
