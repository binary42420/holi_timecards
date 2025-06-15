"""
Trash Bin Handlers for Soft Delete Operations
Handles getting, restoring, and permanently deleting soft-deleted items
"""

import logging
from datetime import datetime
from sqlalchemy import and_, or_
from db.models import User, Job, Shift, ClientCompany
from main import get_db_session

logger = logging.getLogger(__name__)

def handle_get_deleted_items(data, user_session):
    """Get all deleted items (Request ID 701)"""
    try:
        if not user_session or not user_session.is_manager:
            return {
                "request_id": 701,
                "success": False,
                "error": "Manager access required"
            }

        with get_db_session() as session:
            deleted_items = []

            # Get deleted users
            deleted_users = session.query(User).filter(User.is_deleted == True).all()
            for user in deleted_users:
                deleted_items.append({
                    "id": user.id,
                    "type": "user",
                    "name": f"{user.first_name} {user.last_name}",
                    "description": f"Email: {user.email or 'N/A'}",
                    "deleted_at": user.deleted_at.isoformat() if user.deleted_at else None
                })

            # Get deleted jobs
            deleted_jobs = session.query(Job).filter(Job.is_deleted == True).all()
            for job in deleted_jobs:
                deleted_items.append({
                    "id": job.id,
                    "type": "job",
                    "name": job.name,
                    "description": f"Venue: {job.venue_name or 'N/A'}",
                    "deleted_at": job.deleted_at.isoformat() if job.deleted_at else None
                })

            # Get deleted shifts
            deleted_shifts = session.query(Shift).filter(Shift.is_deleted == True).all()
            for shift in deleted_shifts:
                job_name = shift.job.name if shift.job else "Unknown Job"
                deleted_items.append({
                    "id": shift.id,
                    "type": "shift",
                    "name": f"{job_name} - {shift.shift_description or 'Shift'}",
                    "description": f"Date: {shift.start_time.strftime('%Y-%m-%d') if shift.start_time else 'N/A'}",
                    "deleted_at": shift.deleted_at.isoformat() if shift.deleted_at else None
                })

            # Get deleted clients
            deleted_clients = session.query(ClientCompany).filter(ClientCompany.is_deleted == True).all()
            for client in deleted_clients:
                deleted_items.append({
                    "id": client.id,
                    "type": "client",
                    "name": client.name,
                    "description": f"Contact: {getattr(client, 'contact_email', 'N/A')}",
                    "deleted_at": client.deleted_at.isoformat() if client.deleted_at else None
                })

            return {
                "request_id": 701,
                "success": True,
                "data": deleted_items
            }

    except Exception as e:
        logger.error(f"Error getting deleted items: {e}")
        return {
            "request_id": 701,
            "success": False,
            "error": f"Failed to get deleted items: {str(e)}"
        }

def handle_restore_item(data, user_session):
    """Restore a single deleted item (Request ID 702)"""
    try:
        if not user_session or not user_session.is_manager:
            return {
                "request_id": 702,
                "success": False,
                "error": "Manager access required"
            }

        item_id = data.get('item_id')
        item_type = data.get('item_type')

        if not item_id or not item_type:
            return {
                "request_id": 702,
                "success": False,
                "error": "item_id and item_type are required"
            }

        with get_db_session() as session:
            # Get the appropriate model
            model_map = {
                'user': User,
                'job': Job,
                'shift': Shift,
                'client': ClientCompany
            }

            if item_type not in model_map:
                return {
                    "request_id": 702,
                    "success": False,
                    "error": f"Invalid item type: {item_type}"
                }

            Model = model_map[item_type]
            item = session.query(Model).filter(
                and_(Model.id == item_id, Model.is_deleted == True)
            ).first()

            if not item:
                return {
                    "request_id": 702,
                    "success": False,
                    "error": f"Deleted {item_type} with ID {item_id} not found"
                }

            # Restore the item
            item.is_deleted = False
            item.deleted_at = None
            session.commit()

            return {
                "request_id": 702,
                "success": True,
                "message": f"{item_type.capitalize()} restored successfully"
            }

    except Exception as e:
        logger.error(f"Error restoring item: {e}")
        return {
            "request_id": 702,
            "success": False,
            "error": f"Failed to restore item: {str(e)}"
        }

def handle_bulk_restore_items(data, user_session):
    """Restore multiple deleted items (Request ID 703)"""
    try:
        if not user_session or not user_session.is_manager:
            return {
                "request_id": 703,
                "success": False,
                "error": "Manager access required"
            }

        items = data.get('items', [])
        if not items:
            return {
                "request_id": 703,
                "success": False,
                "error": "No items provided for restoration"
            }

        with get_db_session() as session:
            model_map = {
                'user': User,
                'job': Job,
                'shift': Shift,
                'client': ClientCompany
            }

            restored_count = 0
            errors = []

            for item_data in items:
                item_id = item_data.get('item_id')
                item_type = item_data.get('item_type')

                if not item_id or not item_type:
                    errors.append(f"Invalid item data: {item_data}")
                    continue

                if item_type not in model_map:
                    errors.append(f"Invalid item type: {item_type}")
                    continue

                try:
                    Model = model_map[item_type]
                    item = session.query(Model).filter(
                        and_(Model.id == item_id, Model.is_deleted == True)
                    ).first()

                    if item:
                        item.is_deleted = False
                        item.deleted_at = None
                        restored_count += 1
                    else:
                        errors.append(f"Deleted {item_type} with ID {item_id} not found")

                except Exception as e:
                    errors.append(f"Error restoring {item_type} {item_id}: {str(e)}")

            session.commit()

            return {
                "request_id": 703,
                "success": True,
                "message": f"Restored {restored_count} items",
                "restored_count": restored_count,
                "errors": errors if errors else None
            }

    except Exception as e:
        logger.error(f"Error bulk restoring items: {e}")
        return {
            "request_id": 703,
            "success": False,
            "error": f"Failed to bulk restore items: {str(e)}"
        }

def handle_permanent_delete_item(data, user_session):
    """Permanently delete an item (Request ID 704)"""
    try:
        if not user_session or not user_session.is_manager:
            return {
                "request_id": 704,
                "success": False,
                "error": "Manager access required"
            }

        item_id = data.get('item_id')
        item_type = data.get('item_type')

        if not item_id or not item_type:
            return {
                "request_id": 704,
                "success": False,
                "error": "item_id and item_type are required"
            }

        with get_db_session() as session:
            model_map = {
                'user': User,
                'job': Job,
                'shift': Shift,
                'client': ClientCompany
            }

            if item_type not in model_map:
                return {
                    "request_id": 704,
                    "success": False,
                    "error": f"Invalid item type: {item_type}"
                }

            Model = model_map[item_type]
            item = session.query(Model).filter(
                and_(Model.id == item_id, Model.is_deleted == True)
            ).first()

            if not item:
                return {
                    "request_id": 704,
                    "success": False,
                    "error": f"Deleted {item_type} with ID {item_id} not found"
                }

            # Permanently delete the item
            session.delete(item)
            session.commit()

            return {
                "request_id": 704,
                "success": True,
                "message": f"{item_type.capitalize()} permanently deleted"
            }

    except Exception as e:
        logger.error(f"Error permanently deleting item: {e}")
        return {
            "request_id": 704,
            "success": False,
            "error": f"Failed to permanently delete item: {str(e)}"
        }

def handle_soft_delete_job(data, user_session):
    """Soft delete a job (Request ID 705)"""
    try:
        if not user_session or not user_session.is_manager:
            return {
                "request_id": 705,
                "success": False,
                "error": "Manager access required"
            }

        job_id = data.get('job_id')
        if not job_id:
            return {
                "request_id": 705,
                "success": False,
                "error": "job_id is required"
            }

        with get_db_session() as session:
            job = session.query(Job).filter(Job.id == job_id).first()

            if not job:
                return {
                    "request_id": 705,
                    "success": False,
                    "error": f"Job with ID {job_id} not found"
                }

            if job.is_deleted:
                return {
                    "request_id": 705,
                    "success": False,
                    "error": "Job is already deleted"
                }

            # Soft delete the job
            job.is_deleted = True
            job.deleted_at = datetime.now()
            session.commit()

            return {
                "request_id": 705,
                "success": True,
                "message": f"Job '{job.name}' moved to trash"
            }

    except Exception as e:
        logger.error(f"Error soft deleting job: {e}")
        return {
            "request_id": 705,
            "success": False,
            "error": f"Failed to delete job: {str(e)}"
        }
