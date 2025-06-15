from main import get_db_session
from db.controllers.client_companies_controller import ClientCompaniesController


def handle_get_all_client_companies(user_session):
    """
    Handles the request to get all client companies.
    Requires a user session but doesn't strictly need manager privileges for listing,
    though typically job creation (which uses this) is a manager function.
    """
    if not user_session:
        return {"success": False, "error": "User session not found."}

    # if not user_session.can_access_manager_page():
    #     return {"success": False, "error": "User does not have access to this feature."}

    try:
        with get_db_session() as session:
            controller = ClientCompaniesController(session)
            companies = controller.get_all_client_companies()
            return {"request_id": 200, "success": True, "data": companies} # New request_id for this
    except Exception as e:
        print(f"Error in handle_get_all_client_companies: {e}")
        return {"request_id": 200, "success": False, "error": str(e)}


def handle_create_client_company(data, user_session):
    """
    Handles the request to create a new client company.
    Requires manager privileges.
    """
    if not user_session:
        return {"request_id": 201, "success": False, "error": "User session not found."}

    if not user_session.can_access_manager_page():
        return {"request_id": 201, "success": False, "error": "User does not have access to this feature."}

    try:
        company_name = data.get('name', '').strip()
        if not company_name:
            return {"request_id": 201, "success": False, "error": "Company name is required."}

        with get_db_session() as session:
            controller = ClientCompaniesController(session)
            company_data = {"name": company_name}
            new_company = controller.create_entity(company_data)

            return {
                "request_id": 201,
                "success": True,
                "message": "Client company created successfully.",
                "data": {"id": new_company.id, "name": new_company.name}
            }
    except Exception as e:
        print(f"Error in handle_create_client_company: {e}")
        return {"request_id": 201, "success": False, "error": str(e)}


def handle_update_client_company(data, user_session):
    """
    Handles the request to update a client company.
    Requires manager privileges.
    """
    if not user_session:
        return {"request_id": 202, "success": False, "error": "User session not found."}

    if not user_session.can_access_manager_page():
        return {"request_id": 202, "success": False, "error": "User does not have access to this feature."}

    try:
        company_id = data.get('id')
        company_name = data.get('name', '').strip()

        if not company_id:
            return {"request_id": 202, "success": False, "error": "Company ID is required."}

        if not company_name:
            return {"request_id": 202, "success": False, "error": "Company name is required."}

        with get_db_session() as session:
            controller = ClientCompaniesController(session)
            update_data = {"name": company_name}
            updated_company = controller.update_entity(company_id, update_data)

            return {
                "request_id": 202,
                "success": True,
                "message": "Client company updated successfully.",
                "data": {"id": updated_company.id, "name": updated_company.name}
            }
    except Exception as e:
        print(f"Error in handle_update_client_company: {e}")
        return {"request_id": 202, "success": False, "error": str(e)}


def handle_delete_client_company(data, user_session):
    """
    Handles the request to delete a client company.
    Requires manager privileges.
    """
    if not user_session:
        return {"request_id": 203, "success": False, "error": "User session not found."}

    if not user_session.can_access_manager_page():
        return {"request_id": 203, "success": False, "error": "User does not have access to this feature."}

    try:
        company_id = data.get('id')

        if not company_id:
            return {"request_id": 203, "success": False, "error": "Company ID is required."}

        with get_db_session() as session:
            controller = ClientCompaniesController(session)
            controller.delete_entity(company_id)

            return {
                "request_id": 203,
                "success": True,
                "message": "Client company deleted successfully."
            }
    except Exception as e:
        print(f"Error in handle_delete_client_company: {e}")
        return {"request_id": 203, "success": False, "error": str(e)}
