from config.constants import db
from main import get_db_session
from db.controllers.jobs_controller import JobsController
from user_session import UserSession


def handle_create_job(data: dict, user_session: UserSession):
    """
    Handles the request to create a new job with location information.
    Each job represents a specific project at a specific venue.
    data should include: name, client_company_id, venue_name, venue_address
    """
    if not user_session:
        return {"success": False, "error": "User session not found."}
    if not user_session.can_access_manager_page():
        return {"success": False, "error": "User does not have manager privileges."}

    # Required fields
    job_name = data.get("name")
    client_company_id = data.get("client_company_id")
    venue_name = data.get("venue_name")
    venue_address = data.get("venue_address")

    if not all([job_name, client_company_id, venue_name, venue_address]):
        return {"request_id": 210, "success": False, "error": "name, client_company_id, venue_name, and venue_address are required."}

    try:
        with get_db_session() as session:

            controller = JobsController(session)
        job_data = {
            "name": job_name,
            "client_company_id": int(client_company_id),
            "venue_name": venue_name,
            "venue_address": venue_address,
            "venue_contact_info": data.get("venue_contact_info"),
            "description": data.get("description"),
            "estimated_start_date": data.get("estimated_start_date"),
            "estimated_end_date": data.get("estimated_end_date"),
            "created_by": user_session.get_id
        }
        print(f"Creating job with data: {job_data}")
        created_job = controller.create_job(job_data)
        print(f"Job created successfully: {created_job}")

        # Verify the job was actually saved by trying to retrieve it
        all_jobs = controller.get_all_active_jobs()
        print(f"All jobs for Hands on Labor: {all_jobs}")

        return {"request_id": 210, "success": True, "data": created_job}
    except Exception as e:
        print(f"Error in handle_create_job: {e}")
        import traceback
        traceback.print_exc()
        return {"request_id": 210, "success": False, "error": str(e)}


def handle_get_jobs_by_manager(user_session: UserSession):
    """
    Handles the request to get all jobs for Hands on Labor.
    All managers can see and manage all jobs since there's only one company.
    """
    if not user_session:
        return {"success": False, "error": "User session not found."}
    if not user_session.can_access_manager_page():
        return {"success": False, "error": "User does not have manager privileges."}

    try:
        with get_db_session() as session:

            controller = JobsController(session)
        print(f"Fetching all jobs for Hands on Labor")
        jobs = controller.get_all_active_jobs()
        print(f"Found {len(jobs)} jobs: {jobs}")
        return {"request_id": 211, "success": True, "data": jobs}
    except Exception as e:
        print(f"Error in handle_get_jobs_by_manager: {e}")
        import traceback
        traceback.print_exc()
        return {"request_id": 211, "success": False, "error": str(e)}


def handle_update_job(data: dict, user_session: UserSession):
    """
    Handles the request to update an existing job.
    data should include: job_id, and any fields to update (name, client_company_id, venue_name, venue_address, etc.)
    """
    print(f"DEBUG: handle_update_job called with data: {data}")

    if not user_session:
        return {"request_id": 213, "success": False, "error": "User session not found."}
    if not user_session.can_access_manager_page():
        return {"request_id": 213, "success": False, "error": "User does not have manager privileges."}

    # Check if this is actually a client user status update request (common confusion)
    if "user_id" in data and "action" in data:
        print("WARNING: Received user_id and action in job update request. This should be request_id 214, not 213.")
        return {
            "request_id": 213,
            "success": False,
            "error": "Invalid request: This appears to be a client user status update. Please use request_id 214 for client user management."
        }

    # Required field
    job_id = data.get("job_id")
    if not job_id:
        return {"request_id": 213, "success": False, "error": "job_id is required for job updates."}

    try:
        with get_db_session() as session:
            controller = JobsController(session)

            # Get the existing job
            existing_job = controller.get_entity(job_id)
            if not existing_job:
                return {"request_id": 213, "success": False, "error": "Job not found."}

            # Prepare update data - only include fields that are provided
            update_data = {}

            # Optional fields that can be updated
            if "name" in data:
                update_data["name"] = data["name"]
            if "client_company_id" in data:
                update_data["client_company_id"] = data["client_company_id"]
            if "venue_name" in data:
                update_data["venue_name"] = data["venue_name"]
            if "venue_address" in data:
                update_data["venue_address"] = data["venue_address"]
            if "venue_contact_info" in data:
                update_data["venue_contact_info"] = data["venue_contact_info"]
            if "description" in data:
                update_data["description"] = data["description"]
            if "is_active" in data:
                update_data["is_active"] = data["is_active"]

            if not update_data:
                return {"request_id": 213, "success": False, "error": "No valid fields provided for update."}

            print(f"Updating job {job_id} with data: {update_data}")
            updated_job = controller.update_entity(job_id, update_data)
            print(f"Job updated successfully: {updated_job}")

            return {"request_id": 213, "success": True, "data": updated_job}
    except Exception as e:
        print(f"Error in handle_update_job: {e}")
        import traceback
        traceback.print_exc()
        return {"request_id": 213, "success": False, "error": str(e)}
