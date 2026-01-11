from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from threading import Lock
from typing import Optional

from extracto.common.config.config_store import ConfigStore
from extracto.logger.log_utils import Logger

logger = Logger()


class DBConnection:
    _instance: Optional['DBConnection'] = None
    _lock = Lock()

    def __new__(cls, **kwargs):
        """
        Singleton pattern with thread safety for connection pooling
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__name__(cls)
                    cls._instance._initialized = False

    def __init__(self, **kwargs):
        """
        Initialize the database connection class with connection pooling.

        :param db_type: The type of the database (e.g., 'postgresql', 'mysql', 'sqlite').
        :param username: The username for the database.
        :param password: The password for the database.
        :param host: The host of the database server.
        :param port: The port of the database server.
        :param database: The name of the database.
        :param kwargs: Additional arguments for the connection string.
        """

        if self._initialized:
            return

        db_config = ConfigStore().__getattr__("DB")
        self.db_type = db_config.DB_DRIVER_NAME
        self.username = db_config.DB_USERNAME
        self.password = db_config.DB_PASSWORD
        self.host = db_config.DB_HOST
        self.port = db_config.DB_PORT
        self.database = db_config.DB_DATABASE
        self.kwargs = kwargs

        self.connection_string = (
                f"{self.db_type}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
            )
        self.engine = None
        self.Session = None
        self._connect()
        self._initialized = None

    def _connect(self):
        """
        Establish the connection to the database using SQLAlchemy with connection pooling.
        """
        try:

            if self.kwargs:
                params = "&".join(f"{key}={value}" for key, value in self.kwargs.items())
                self.connection_string += f"?{params}"

            logger.info(f"Connecting to database: {self.db_type}://{self.host}:{self.port}/{self.database}")

            self.engine = self._create_engine()
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Database connection established with connection pooling.")
        except SQLAlchemyError as e:
            logger.error(f"Error connecting to the database: {e}")
            raise

    def _create_engine(self):
        """
        Create engine with connection pooling.
        """
        engine = create_engine(
            self.connection_string,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=False
        )
        return engine

    def get_session(self) -> Session:
        """
        Get a new session from the sessionmaker.

        :return: A SQLAlchemy session.
        """
        if not self.Session:
            raise Exception("Database connection is not established.")
        return self.Session()
    
    @contextmanager
    def session_scope(self):
        """
        Provide a transactional scope for database operations.
        Usage:
            with DBConnection().session_scope() as session:
                # do work
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close_connection(self):
        """
        Close the database connection and dispose of the pool.
        """
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed and pool discposed.")


# Usage Example
# if __name__ == "__main__":
#     db_config = {
#         "db_type": "postgresql",
#         "username": "postgres",
#         "password": "postgres",
#         "host": "localhost",
#         "port": 6432,
#         "database": "private-markets",
#     }
#     from extracto.db.model import Document
#
#     db_connection = DBConnection()
#     db_connection.connect()
#
#
#     # Get a.py session and perform database operations
#     session = db_connection.get_session()
#     import  pdb; pdb.set_trace()
#
#     try:
#         result = session.query(Document).all()
#         logger.info(f"result: {result}")
#     except Exception as e:
#         logger.error(f"Error during database operation: {e}")
#     finally:
#         session.close()
#         db_connection.close_connection()
