import datetime

# Define the next_sunday function to be used as the default value
def _calculate_next_sunday():
    today = datetime.date.today()
    days_until_sunday = (6 - today.weekday() + 7) % 7
    return today + datetime.timedelta(days=days_until_sunday)

next_sunday = _calculate_next_sunday()

DAYS_OF_WEEK = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# TEMPORARY COMPATIBILITY LAYER
# This provides the old 'db' variable for backward compatibility
# while we transition to proper session management
try:
    from main import create_session
    db = create_session()
    print("✅ Temporary db session created for backward compatibility")
except Exception as e:
    print(f"⚠️  Could not create temporary db session: {e}")
    db = None

# The global 'db' session is being phased out.
# New code should call main.create_session() from main.py
# Example in a handler:
# from main import create_session
# db_session = create_session()
# try:
#     # ... use db_session ...
#     db_session.commit() # if changes were made
# except:
#     db_session.rollback()
#     raise
# finally:
#     db_session.close()
