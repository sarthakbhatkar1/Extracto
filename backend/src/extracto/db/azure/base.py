from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from extracto.common.config.config_store import ConfigStore
from extracto.logger.log_utils import Logger

logger = Logger()

class DBConnection:
    def __init__(self, **kwargs):
        """
        Initialize the database connection class.

        :param db_type: The type of the database (e.g., 'postgresql', 'mysql', 'sqlite').
        :param username: The username for the database.
        :param password: The password for the database.
        :param host: The host of the database server.
        :param port: The port of the database server.
        :param database: The name of the database.
        :param kwargs: Additional arguments for the connection string.
        """

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

    def connect(self):
        """
        Establish the connection to the database using SQLAlchemy.
        """
        try:

            if self.kwargs:
                params = "&".join(f"{key}={value}" for key, value in self.kwargs.items())
                self.connection_string += f"?{params}"

            print(f"self.connection_string: {self.connection_string}")

            self.engine = self._create_engine()
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Database connection established.")
        except SQLAlchemyError as e:
            logger.error(f"Error connecting to the database: {e}")
            raise

    def _create_engine(self):
        self.engine = create_engine(self.connection_string)
        return self.engine

    def get_session(self):
        """
        Get a.py new session from the sessionmaker.

        :return: A SQLAlchemy session.
        """
        self.connect()
        if not self.Session:
            raise Exception("Database connection is not established. Call `connect()` first.")
        return self.Session()

    def close_connection(self):
        """
        Close the database connection.
        """
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed.")


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
