# core/logger.py
import logging
from datetime import datetime
from functools import wraps
from fastapi import Request
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('activity.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def log_activity(endpoint_name: str):
    """Decorator to log activity"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = datetime.now()

            # Extract user info from request if available
            user_info = "Unauthenticated"
            for arg in args:
                if hasattr(arg, 'aadhaar_number'):
                    user_info = f"User: {arg.aadhaar_number}"
                elif hasattr(arg, 'id') and hasattr(arg, 'name'):
                    user_info = f"Agency: {arg.id}"
                elif isinstance(arg, Request):
                    # Try to get token from request
                    auth_header = arg.headers.get('Authorization', '')
                    if auth_header:
                        user_info = f"Token: {auth_header[:20]}..."

            # Log start
            logger.info(
                f"[START] {endpoint_name} | {user_info} | Time: {start_time}")

            try:
                result = await func(*args, **kwargs)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                # Log success
                logger.info(
                    f"[SUCCESS] {endpoint_name} | {user_info} | Duration: {duration:.2f}s | Status: Success")
                return result

            except Exception as e:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                # Log error
                logger.error(
                    f"[ERROR] {endpoint_name} | {user_info} | Duration: {duration:.2f}s | Error: {str(e)}")
                raise

        return wrapper
    return decorator


class ActivityLogger:
    """Simple activity logger class"""

    @staticmethod
    def log_user_action(user_id: str, action: str, details: dict = None):
        """Log user action"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "user_type": "user",
            "user_id": user_id,
            "action": action,
            "details": details or {}
        }
        logger.info(json.dumps(log_entry))

    @staticmethod
    def log_agency_action(agency_id: str, action: str, details: dict = None):
        """Log agency action"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "user_type": "agency",
            "user_id": agency_id,
            "action": action,
            "details": details or {}
        }
        logger.info(json.dumps(log_entry))

    @staticmethod
    def log_request_creation(user_id: str, agency_id: str, request_id: str, new_address: str):
        """Log request creation"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "user_type": "user",
            "user_id": user_id,
            "action": "CREATE_REQUEST",
            "details": {
                "agency_id": agency_id,
                "request_id": request_id,
                "new_address": new_address
            }
        }
        logger.info(json.dumps(log_entry))

    @staticmethod
    def log_request_update(agency_id: str, request_id: str, status: str, reason: str = None):
        """Log request status update"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "user_type": "agency",
            "user_id": agency_id,
            "action": f"UPDATE_REQUEST_{status.upper()}",
            "details": {
                "request_id": request_id,
                "status": status,
                "reason": reason
            }
        }
        logger.info(json.dumps(log_entry))

    @staticmethod
    def log_request_cancellation(user_id: str, request_id: str):
        """Log request cancellation"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "user_type": "user",
            "user_id": user_id,
            "action": "CANCEL_REQUEST",
            "details": {
                "request_id": request_id
            }
        }
        logger.info(json.dumps(log_entry))

    @staticmethod
    def log_login(user_type: str, user_id: str):
        """Log user/agency login"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "user_type": user_type,
            "user_id": user_id,
            "action": "LOGIN",
            "details": {}
        }
        logger.info(json.dumps(log_entry))

    @staticmethod
    def log_registration(user_type: str, user_id: str, name: str):
        """Log user/agency registration"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "user_type": user_type,
            "user_id": user_id,
            "action": "REGISTER",
            "details": {
                "name": name
            }
        }
        logger.info(json.dumps(log_entry))
