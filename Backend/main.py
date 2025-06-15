import os
import time
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, DisconnectionError
from db.models import Base # Assuming Base is correctly defined in db.models

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_engine = None
_session_factory = None
_initialization_error = None

def get_database_password():
    """Get database password from environment variable or fallback to config file"""
    # First try environment variable (for Cloud Run deployment)
    db_password = os.getenv("DB_PASSWORD")
    if db_password:
        logger.info("Using database password from environment variable")
        return db_password

    # Fallback to config file (for local development)
    try:
        from config.private_password import PASSWORD
        logger.info("Using database password from config file")
        return PASSWORD
    except ImportError:
        logger.error("No database password found in environment variable or config file")
        raise RuntimeError("Database password not configured. Set DB_PASSWORD environment variable or create config/private_password.py")

def initialize_database_and_session_factory():
    global _engine, _session_factory, _initialization_error

    if _engine and _session_factory:
        print("✅ Database engine and session factory already initialized.")
        return

    DB_HOST = os.getenv("DB_HOST", "miano.h.filess.io")
    DB_PORT = os.getenv("DB_PORT", "3305")
    DB_USER = os.getenv("DB_USER", "holitimecards_main")
    DB_NAME = os.getenv("DB_NAME", "holitimecards_main")

    try:
        DB_PASSWORD = get_database_password()
    except Exception as e:
        _initialization_error = e
        print(f"❌ Failed to get database password: {e}")
        return

    connection_url = f'mariadb+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    print(f"Attempting to initialize database engine: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

    try:
        engine = create_engine(
            connection_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            connect_args={
                'connect_timeout': 30,
                'read_timeout': 30,
                'write_timeout': 30,
                'charset': 'utf8mb4'
            }
        )

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("✅ Database engine connection successful.")
        
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("✅ Database tables created/verified successfully.")

        _engine = engine
        _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        _initialization_error = None
        print("✅ Database engine and session factory initialized successfully.")

    except Exception as e:
        _initialization_error = e
        print(f"❌ Database engine or session factory initialization failed: {e}")
        print(f"❌ Error type: {type(e).__name__}")

def get_engine():
    if not _engine and not _initialization_error:
        initialize_database_and_session_factory()
    if _initialization_error:
        raise RuntimeError(f"Database not initialized due to previous error: {_initialization_error}")
    if not _engine:
        raise RuntimeError("Database engine could not be initialized and no specific error was caught.")
    return _engine

def create_session():
    """
    Creates and returns a new SQLAlchemy session from the factory.
    Attempts to initialize the factory if it hasn't been already.
    """
    global _session_factory, _initialization_error

    if not _session_factory and not _initialization_error:
        print("Session factory not initialized. Attempting to initialize now...")
        initialize_database_and_session_factory()

    if _initialization_error:
        raise RuntimeError(f"Cannot create session: Database initialization failed: {_initialization_error}")
    if not _session_factory:
        raise RuntimeError("Cannot create session: Session factory could not be initialized.")

    return _session_factory()


def initialize_database_and_session():
    """
    Legacy function for backward compatibility.
    Returns (session, engine) tuple.
    """
    initialize_database_and_session_factory()
    session = create_session()
    engine = get_engine()
    return session, engine


def get_database_session():
    """
    Legacy function for backward compatibility.
    Returns a database session.
    """
    return create_session()


@contextmanager
def get_db_session():
    """
    Context manager for database sessions with retry logic.
    Ensures proper session cleanup and error handling.

    Usage:
        with get_db_session() as session:
            # Use session here
            session.query(User).all()
            session.commit()  # if needed
    """
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        session = None
        try:
            session = create_session()
            yield session
            session.commit()  # Auto-commit if no exception
            break  # Success, exit retry loop

        except (OperationalError, DisconnectionError) as e:
            if session:
                session.rollback()
                session.close()

            if attempt < max_retries - 1:
                logger.warning(f"Database connection error (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            else:
                logger.error(f"Database connection failed after {max_retries} attempts: {e}")
                raise

        except Exception as e:
            if session:
                session.rollback()
                session.close()
            logger.error(f"Database session error: {e}")
            raise

        finally:
            if session:
                session.close()  # Always close the session

if _engine is None and _session_factory is None:
    try:
        print("Initial attempt to initialize database and session factory from main.py module load...")
        initialize_database_and_session_factory()
    except Exception as e:
        print(f"⚠️ Initial attempt to initialize database failed during module load: {e}. Will retry on first session request.")
