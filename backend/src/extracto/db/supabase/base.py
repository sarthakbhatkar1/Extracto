from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import urllib.parse

from extracto.common.config.config_store import ConfigStore
from extracto.logger.log_utils import Logger

logger = Logger()


class DBConnection:
    def __init__(self, **kwargs):
        """
        Initialize the database connection class for Supabase PostgreSQL.

        :param kwargs: Additional arguments for the connection string (e.g., sslmode, connect_timeout).
        """
        db_config = ConfigStore().__getattr__("DB")
        self.db_type = db_config.DB_DRIVER_NAME
        self.username = db_config.DB_USERNAME
        self.password = urllib.parse.quote(db_config.DB_PASSWORD)  # URL-encode password
        self.host = db_config.DB_HOST
        self.port = db_config.DB_PORT  # Use 6543 for transaction mode or 5432 for session mode
        self.database = db_config.DB_DATABASE

        # Define default kwargs and update with provided kwargs
        self.kwargs = {"sslmode": "require", "connect_timeout": 30}
        # Update with provided kwargs, ensuring connect_timeout is an integer
        for key, value in kwargs.items():
            if key == "connect_timeout":
                try:
                    self.kwargs[key] = int(value)  # Force integer for connect_timeout
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid connect_timeout value: {value}. Must be an integer.")
            else:
                self.kwargs[key] = value

        # Construct Supabase-compatible connection string
        self.connection_string = (
            f"{self.db_type}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        )
        self.engine = None
        self.Session = None

    def connect(self):
        """
        Establish the connection to the Supabase database using SQLAlchemy.
        """
        try:
            # Add valid parameters to the connection string
            valid_params = {
                k: v for k, v in self.kwargs.items()
                if k in ["sslmode", "connect_timeout"] and v is not None
            }
            if valid_params:
                params = "&".join(f"{key}={urllib.parse.quote(str(value))}" for key, value in valid_params.items())
                final_connection_string = f"{self.connection_string}?{params}"
            else:
                final_connection_string = self.connection_string

            self.engine = create_engine(
                final_connection_string,
                pool_pre_ping=True,  # Pings DB on checkout to detect dead connections
                pool_recycle=300,  # Recycles connections older than 300s
                pool_timeout=20,  # Timeout for pool checkout
                pool_size=5,  # Max connections in pool
                max_overflow=10  # Allow temporary overflow
            )
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Supabase database connection established.")
        except SQLAlchemyError as e:
            logger.error(f"Error connecting to the Supabase database: {e}")
            raise

    def _create_engine(self):
        """
        Create and return a SQLAlchemy engine for the Supabase database.
        """
        return create_engine(self.connection_string)

    def get_session(self):
        """
        Get a new session from the sessionmaker.

        :return: A SQLAlchemy session.
        """
        self.connect()
        if not self.Session:
            raise Exception("Supabase database connection is not established. Call `connect()` first.")
        return self.Session()

    def close_connection(self):
        """
        Close the Supabase database connection.
        """
        if self.engine:
            self.engine.dispose()
            logger.info("Supabase database connection closed.")

#
# # Usage Example
# if __name__ == "__main__":
#     # db_config = {
#     #     "db_type": "postgresql+psycopg2",
#     #     "username": "postgres",
#     #     "password": "your-supabase-password",  # Replace with your Supabase password
#     #     "host": "cvxnivhbhmsaoulcjjzf.supabase.co",  # Replace with your Supabase host
#     #     "port": 6543,  # Use transaction mode
#     #     "database": "postgres",
#     # }
#     from extracto.db.model import Document
#
#     # Initialize with SSL and timeout
#     conn_str = "postgresql://postgres:Vandana30Sarth@db.cvxnivhbhmsaoulcjjzf.supabase.co:5432/postgres"
#     conn_str = "postgresql+psycopg2://postgres:Vandana30Sarth@cvxnivhbhmsaoulcjjzf.supabase.co:6543/extracto?sslmode=require&connect_timeout=30"
#     db_connection = DBConnection(sslmode="require", connect_timeout=30)
#     db_connection.connect()
#
#     # DATABASE_URL = f"postgresql+psycopg2://postgres:Vandana30Sarth@db.cvxnivhbhmsaoulcjjzf.supabase.co:5432/postgres?sslmode=require"
#
#     # Get a session and perform database operations
#     session = db_connection.get_session()
#
#     try:
#         result = session.query(Document).all()
#         logger.info(f"result: {result}")
#     except Exception as e:
#         logger.error(f"Error during database operation: {e}")
#     finally:
#         session.close()
#         db_connection.close_connection()
#