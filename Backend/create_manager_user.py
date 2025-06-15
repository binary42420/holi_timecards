import sys
import os

# Adjust the Python path to include the parent directory (Backend)
# This allows imports like 'from db.controllers...' to work when the script is run directly.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) # This should be EasyShifts if Backend is one level down
# If Backend is the root for these modules, then current_dir is fine.
# For running from within Backend, current_dir is usually added to sys.path by Python itself.
# However, to be explicit and handle different execution contexts:
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if project_root not in sys.path and os.path.basename(current_dir) == "Backend":
    # If we are in Backend, and EasyShifts is the project root containing Backend as a package
    # this line might not be strictly necessary if Backend itself is the root for its internal modules.
    # For now, let's assume Backend is the root for its modules.
    pass


from db.controllers.users_controller import UsersController
from main import create_session

def create_manager():
    """
    Prompts for manager details and creates a new manager user in the database.
    """
    # Use proper database session management
    db_session = create_session()
    if not db_session:
        print("Database session not initialized. Please check your main.py and constants.py.")
        return

    try:
        users_controller = UsersController(db_session)

        print("Creating a new manager user...")
        username = input("Enter username for the manager: ")
        password = input("Enter password for the manager: ")
        name = input("Enter the name for the manager (this will also be the workplace name): ")

        user_data = {
            "username": username,
            "password": password,
            "isManager": True,
            "isAdmin": False,  # Assuming managers are not admins by default, adjust if needed
            "client_company_id": None, # Assuming agency manager, not a client representative
            "isActive": True,    # Managers are active by default
            "isApproval": True,  # Managers are approved by default
            "name": name,
            "employee_type": None # Or a specific EmployeeType if managers have one
        }

        # Check if username already exists
        if users_controller.check_username_existence(username):
            print(f"Error: Username '{username}' already exists. Please choose a different username.")
            return

        created_user = users_controller.create_entity(user_data)
        if created_user:
            print(f"Manager user '{created_user.username}' (ID: {created_user.id}) created successfully.")
            db_session.commit()
            # Note: The WorkPlace entry for a manager (linking their ID to their own ID as workPlaceID)
            # is typically handled during manager sign-in or a separate setup step.
            # This script only creates the User record.
        else:
            print("Failed to create manager user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        db_session.rollback()
    finally:
        db_session.close()

if __name__ == "__main__":
    # Ensure the db session from constants is used, which should be initialized when constants.py is imported.
    # The initialize_database_and_session() might be called again if constants.py didn't fully set it up
    # or if you prefer an explicit session for this script.
    # For simplicity, we rely on constants.py having done its job.
    if not db_session:
        print("Attempting to initialize database session for script execution...")
        temp_db, _ = initialize_database_and_session_factory()
        if temp_db:
            # This is tricky because the db_session in constants is what controllers use.
            # Overwriting it here might not be ideal. Best to ensure constants.py initializes it.
            print("DB session was not available from constants, but a temporary one was created.")
            print("Please ensure constants.py correctly initializes the 'db' variable.")
            # For the script to run standalone if constants.py didn't init:
            # users_controller = UsersController(temp_db) # Re-init controller with this session
            # ... then proceed with user creation using this controller.
            # However, the provided script structure relies on the global 'db_session' from constants.
        else:
            print("Failed to initialize a database session for the script.")
            exit(1)
            
    create_manager()
    
    if db_session: # If using the global session from constants.py
        db_session.close()
