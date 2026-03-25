# # routers/requests.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from core.database import get_db
# from models.request import AddressRequest
# from models.user import User
# from models.agency import Agency
# from services.auth import get_current_user, get_current_agency

# router = APIRouter(prefix="/requests", tags=["Requests"])


# @router.post("/create")
# def create_request(request_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     # Check if agency exists
#     agency = db.query(Agency).filter(
#         Agency.id == request_data["agency_id"]).first()
#     if not agency:
#         raise HTTPException(status_code=404, detail="Agency not found")

#     # Create request
#     new_request = AddressRequest(
#         user_aadhaar=current_user.aadhaar_number,
#         agency_id=request_data["agency_id"],
#         new_address=request_data["new_address"]
#     )
#     db.add(new_request)
#     db.commit()
#     db.refresh(new_request)
#     return new_request


# @router.get("/my-requests")
# def get_my_requests(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     requests = db.query(AddressRequest).filter(
#         AddressRequest.user_aadhaar == current_user.aadhaar_number).all()
#     return requests


# @router.get("/agency-requests")
# def get_agency_requests(current_agency: Agency = Depends(get_current_agency), db: Session = Depends(get_db)):
#     requests = db.query(AddressRequest).filter(
#         AddressRequest.agency_id == current_agency.id).all()
#     return requests


# @router.put("/{request_id}")
# def update_request(request_id: str, update_data: dict, current_agency: Agency = Depends(get_current_agency), db: Session = Depends(get_db)):
#     request_obj = db.query(AddressRequest).filter(
#         AddressRequest.id == request_id,
#         AddressRequest.agency_id == current_agency.id
#     ).first()

#     if not request_obj:
#         raise HTTPException(status_code=404, detail="Request not found")

#     request_obj.status = update_data.get("status", request_obj.status)
#     if "reason" in update_data:
#         request_obj.reason = update_data["reason"]

#     db.commit()
#     return {"message": "Request updated", "request": request_obj}


# @router.delete("/{request_id}")
# def cancel_request(request_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     request_obj = db.query(AddressRequest).filter(
#         AddressRequest.id == request_id,
#         AddressRequest.user_aadhaar == current_user.aadhaar_number
#     ).first()

#     if not request_obj:
#         raise HTTPException(status_code=404, detail="Request not found")

#     request_obj.status = "cancelled"
#     db.commit()
#     return {"message": "Request cancelled"}


# @router.get("/pending-requests")
# def get_pending_requests(
#     current_agency: Agency = Depends(get_current_agency),
#     db: Session = Depends(get_db)
# ):
#     """Get pending requests for the current agency"""
#     requests = db.query(AddressRequest).filter(
#         AddressRequest.agency_id == current_agency.id,
#         AddressRequest.status == "pending"
#     ).order_by(AddressRequest.created_at.desc()).all()

#     if not requests:
#         return []  # Return empty list instead of error

#     return [{
#         "id": r.id,
#         "user_aadhaar": r.user_aadhaar,
#         "new_address": r.new_address,
#         "status": r.status,
#         "reason": r.reason,
#         "created_at": r.created_at
#     } for r in requests]


# @router.get("/stats")
# def get_stats(
#     db: Session = Depends(get_db),
#     user: Optional[User] = Depends(get_current_user),
#     agency: Optional[Agency] = Depends(get_current_agency)
# ):
#     """Get statistics about requests"""
#     try:
#         if user:
#             # Stats for user
#             total = db.query(AddressRequest).filter(
#                 AddressRequest.user_aadhaar == user.aadhaar_number
#             ).count()

#             pending = db.query(AddressRequest).filter(
#                 AddressRequest.user_aadhaar == user.aadhaar_number,
#                 AddressRequest.status == "pending"
#             ).count()

#             approved = db.query(AddressRequest).filter(
#                 AddressRequest.user_aadhaar == user.aadhaar_number,
#                 AddressRequest.status == "approved"
#             ).count()

#             rejected = db.query(AddressRequest).filter(
#                 AddressRequest.user_aadhaar == user.aadhaar_number,
#                 AddressRequest.status == "rejected"
#             ).count()

#             cancelled = db.query(AddressRequest).filter(
#                 AddressRequest.user_aadhaar == user.aadhaar_number,
#                 AddressRequest.status == "cancelled"
#             ).count()

#             return {
#                 "total": total,
#                 "pending": pending,
#                 "approved": approved,
#                 "rejected": rejected,
#                 "cancelled": cancelled
#             }

#         elif agency:
#             # Stats for agency
#             total = db.query(AddressRequest).filter(
#                 AddressRequest.agency_id == agency.id
#             ).count()

#             pending = db.query(AddressRequest).filter(
#                 AddressRequest.agency_id == agency.id,
#                 AddressRequest.status == "pending"
#             ).count()

#             approved = db.query(AddressRequest).filter(
#                 AddressRequest.agency_id == agency.id,
#                 AddressRequest.status == "approved"
#             ).count()

#             rejected = db.query(AddressRequest).filter(
#                 AddressRequest.agency_id == agency.id,
#                 AddressRequest.status == "rejected"
#             ).count()

#             cancelled = db.query(AddressRequest).filter(
#                 AddressRequest.agency_id == agency.id,
#                 AddressRequest.status == "cancelled"
#             ).count()

#             return {
#                 "total": total,
#                 "pending": pending,
#                 "approved": approved,
#                 "rejected": rejected,
#                 "cancelled": cancelled
#             }

#         else:
#             raise HTTPException(
#                 status_code=401, detail="Authentication required")

#     except Exception as e:
#         logger.error(f"Error getting stats: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


# routers/requests.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from core.database import get_db
from models.request import AddressRequest
from models.user import User
from models.agency import Agency
from services.auth import get_current_user, get_current_agency
from core.logging import logger
import uuid

router = APIRouter(prefix="/requests", tags=["Requests"])


@router.post("/create")
def create_request(
    request_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new address change request"""
    try:
        # Check if agency exists
        agency = db.query(Agency).filter(
            Agency.id == request_data["agency_id"]).first()
        if not agency:
            raise HTTPException(status_code=404, detail="Agency not found")

        # Check for existing pending request
        existing = db.query(AddressRequest).filter(
            AddressRequest.user_aadhaar == current_user.aadhaar_number,
            AddressRequest.agency_id == request_data["agency_id"],
            AddressRequest.status == "pending"
        ).first()

        if existing:
            raise HTTPException(
                status_code=400, detail="You already have a pending request with this agency")

        # Create request
        new_request = AddressRequest(
            id=str(uuid.uuid4())[:8],
            user_aadhaar=current_user.aadhaar_number,
            agency_id=request_data["agency_id"],
            new_address=request_data["new_address"],
            status="pending"
        )
        db.add(new_request)
        db.commit()
        db.refresh(new_request)

        return {
            "id": new_request.id,
            "user_aadhaar": new_request.user_aadhaar,
            "agency_id": new_request.agency_id,
            "new_address": new_request.new_address,
            "status": new_request.status,
            "created_at": new_request.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-requests")
def get_my_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all requests for the current user"""
    try:
        requests = db.query(AddressRequest).filter(
            AddressRequest.user_aadhaar == current_user.aadhaar_number
        ).order_by(AddressRequest.created_at.desc()).all()

        return [{
            "id": r.id,
            "agency_id": r.agency_id,
            "new_address": r.new_address,
            "status": r.status,
            "reason": r.reason,
            "created_at": r.created_at
        } for r in requests]
    except Exception as e:
        logger.error(f"Error getting user requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agency-requests")
def get_agency_requests(
    current_agency: Agency = Depends(get_current_agency),
    db: Session = Depends(get_db)
):
    """Get all requests for the current agency"""
    try:
        requests = db.query(AddressRequest).filter(
            AddressRequest.agency_id == current_agency.id
        ).order_by(AddressRequest.created_at.desc()).all()

        return [{
            "id": r.id,
            "user_aadhaar": r.user_aadhaar,
            "new_address": r.new_address,
            "status": r.status,
            "reason": r.reason,
            "created_at": r.created_at
        } for r in requests]
    except Exception as e:
        logger.error(f"Error getting agency requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending-requests")
def get_pending_requests(
    current_agency: Agency = Depends(get_current_agency),
    db: Session = Depends(get_db)
):
    """Get pending requests for the current agency"""
    try:
        requests = db.query(AddressRequest).filter(
            AddressRequest.agency_id == current_agency.id,
            AddressRequest.status == "pending"
        ).order_by(AddressRequest.created_at.desc()).all()

        return [{
            "id": r.id,
            "user_aadhaar": r.user_aadhaar,
            "new_address": r.new_address,
            "status": r.status,
            "reason": r.reason,
            "created_at": r.created_at
        } for r in requests]
    except Exception as e:
        logger.error(f"Error getting pending requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{request_id}")
def get_request(
    request_id: str,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
    agency: Optional[Agency] = Depends(get_current_agency)
):
    """Get a specific request by ID (if authorized)"""
    try:
        request_obj = db.query(AddressRequest).filter(
            AddressRequest.id == request_id).first()

        if not request_obj:
            raise HTTPException(status_code=404, detail="Request not found")

        # Check authorization
        if user and request_obj.user_aadhaar != user.aadhaar_number:
            raise HTTPException(status_code=403, detail="Not authorized")

        if agency and request_obj.agency_id != agency.id:
            raise HTTPException(status_code=403, detail="Not authorized")

        return {
            "id": request_obj.id,
            "user_aadhaar": request_obj.user_aadhaar,
            "agency_id": request_obj.agency_id,
            "new_address": request_obj.new_address,
            "status": request_obj.status,
            "reason": request_obj.reason,
            "created_at": request_obj.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{request_id}")
def update_request(
    request_id: str,
    update_data: dict,
    current_agency: Agency = Depends(get_current_agency),
    db: Session = Depends(get_db)
):
    """Update request status (approve/reject) - Agency only"""
    try:
        request_obj = db.query(AddressRequest).filter(
            AddressRequest.id == request_id,
            AddressRequest.agency_id == current_agency.id
        ).first()

        if not request_obj:
            raise HTTPException(status_code=404, detail="Request not found")

        if request_obj.status != "pending":
            raise HTTPException(
                status_code=400, detail=f"Cannot update request that is already {request_obj.status}")

        new_status = update_data.get("status")
        if new_status not in ["approved", "rejected"]:
            raise HTTPException(
                status_code=400, detail="Status must be 'approved' or 'rejected'")

        request_obj.status = new_status
        if "reason" in update_data:
            request_obj.reason = update_data["reason"]

        db.commit()

        # If approved, update user's address
        if new_status == "approved":
            user = db.query(User).filter(User.aadhaar_number ==
                                         request_obj.user_aadhaar).first()
            if user:
                user.current_address = request_obj.new_address
                db.commit()
                logger.info(f"Updated address for user {user.aadhaar_number}")

        return {
            "message": f"Request {new_status}",
            "request_id": request_id,
            "status": new_status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{request_id}")
def cancel_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a pending request - User only"""
    try:
        request_obj = db.query(AddressRequest).filter(
            AddressRequest.id == request_id,
            AddressRequest.user_aadhaar == current_user.aadhaar_number
        ).first()

        if not request_obj:
            raise HTTPException(status_code=404, detail="Request not found")

        if request_obj.status != "pending":
            raise HTTPException(
                status_code=400, detail=f"Cannot cancel request that is already {request_obj.status}")

        request_obj.status = "cancelled"
        db.commit()

        return {"message": "Request cancelled", "request_id": request_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
    agency: Optional[Agency] = Depends(get_current_agency)
):
    """Get statistics about requests"""
    try:
        # Check if we have either user or agency
        if not user and not agency:
            raise HTTPException(
                status_code=401, detail="Authentication required")

        if user:
            # Stats for user
            total = db.query(AddressRequest).filter(
                AddressRequest.user_aadhaar == user.aadhaar_number
            ).count()

            pending = db.query(AddressRequest).filter(
                AddressRequest.user_aadhaar == user.aadhaar_number,
                AddressRequest.status == "pending"
            ).count()

            approved = db.query(AddressRequest).filter(
                AddressRequest.user_aadhaar == user.aadhaar_number,
                AddressRequest.status == "approved"
            ).count()

            rejected = db.query(AddressRequest).filter(
                AddressRequest.user_aadhaar == user.aadhaar_number,
                AddressRequest.status == "rejected"
            ).count()

            cancelled = db.query(AddressRequest).filter(
                AddressRequest.user_aadhaar == user.aadhaar_number,
                AddressRequest.status == "cancelled"
            ).count()

            return {
                "type": "user",
                "user_aadhaar": user.aadhaar_number,
                "user_name": user.name,
                "total": total,
                "pending": pending,
                "approved": approved,
                "rejected": rejected,
                "cancelled": cancelled
            }

        elif agency:
            # Stats for agency
            total = db.query(AddressRequest).filter(
                AddressRequest.agency_id == agency.id
            ).count()

            pending = db.query(AddressRequest).filter(
                AddressRequest.agency_id == agency.id,
                AddressRequest.status == "pending"
            ).count()

            approved = db.query(AddressRequest).filter(
                AddressRequest.agency_id == agency.id,
                AddressRequest.status == "approved"
            ).count()

            rejected = db.query(AddressRequest).filter(
                AddressRequest.agency_id == agency.id,
                AddressRequest.status == "rejected"
            ).count()

            cancelled = db.query(AddressRequest).filter(
                AddressRequest.agency_id == agency.id,
                AddressRequest.status == "cancelled"
            ).count()

            return {
                "type": "agency",
                "agency_id": agency.id,
                "agency_name": agency.name,
                "total": total,
                "pending": pending,
                "approved": approved,
                "rejected": rejected,
                "cancelled": cancelled
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting stats: {str(e)}")
