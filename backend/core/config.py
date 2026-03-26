# # core/config.py
# import os
# from typing import List


# class Settings:
#     # Database
#     DATABASE_URL = os.getenv(
#         "DATABASE_URL", "sqlite:///./data/address_sync.db")

#     # Security
#     SECRET_KEY = os.getenv(
#         "SECRET_KEY", "your-secret-key-change-in-production-12345")
#     ALGORITHM = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES = 1440

#     # CORS
#     ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

#     # Application
#     APP_NAME = "Address Sync Service"
#     DEBUG = os.getenv("DEBUG", "True").lower() == "true"

#     # Twilio Settings
#     TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
#     TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
#     TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
#     TWILIO_WHATSAPP_NUMBER = os.getenv(
#         "TWILIO_WHATSAPP_NUMBER", "")  # Optional for WhatsApp

#     # Enable/disable SMS
#     ENABLE_SMS_NOTIFICATIONS = os.getenv(
#         "ENABLE_SMS_NOTIFICATIONS", "True").lower() == "true"


# settings = Settings()


# backend/core/config.py
import os


class Settings:
    # Get the base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'data', 'address_sync.db')}"
    )

    # Security
    SECRET_KEY = os.getenv(
        "SECRET_KEY", "your-secret-key-change-in-production-12345")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 1440

    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

    # Application
    APP_NAME = "Address Sync Service"
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # Twilio (optional)
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
    ENABLE_SMS_NOTIFICATIONS = os.getenv(
        "ENABLE_SMS_NOTIFICATIONS", "False").lower() == "true"


settings = Settings()
