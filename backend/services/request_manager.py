from sqlalchemy.orm import Session
from models.user import User
from models.request import AddressRequest
from core.logging import logger


class RequestManager:
    @staticmethod
    def update_user_address(db: Session, user_aadhaar: str, new_address: str):
        """Update user's address after request approval"""
        try:
            user = db.query(User).filter(
                User.aadhaar_number == user_aadhaar).first()
            if user:
                user.current_address = new_address
                db.commit()
                logger.info(f"Updated address for user {user_aadhaar}")
                return True
        except Exception as e:
            logger.error(
                f"Failed to update address for user {user_aadhaar}: {e}")
            db.rollback()
        return False
