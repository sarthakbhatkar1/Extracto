import os
import boto3
from botocore.exceptions import ClientError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from extracto.common.config.config_store import ConfigStore

# os.environ['ENV'] = "PREDEV"
# os.environ['CONF_PATH'] = r"D:\Projects\career\Extracto\backend\resource"


class DBConnection:
    def __init__(self, config_store=None, use_iam_auth=False):
        """
        Initialize the database connection class for AWS RDS/Aurora.

        Args:
            config_store (ConfigStore, optional): Instance of ConfigStore to retrieve database credentials.
            use_iam_auth (bool): Use IAM database authentication (True) or password (False).
        """
        # Initialize ConfigStore if not provided
        self.engine = None
        self.config = config_store or ConfigStore()

        # Get database credentials (prefer environment variables)
        self.db_type = os.getenv('AWS_DB_AUTH_TYPE', self.config.AWS_DB.AWS_DB_AUTH_TYPE)
        self.username = os.getenv('AWS_DB_USERNAME', self.config.AWS_DB.AWS_DB_USERNAME)
        self.password = None if use_iam_auth else os.getenv('AWS_DB_PASSWORD', self.config.AWS_DB.AWS_DB_PASSWORD)
        self.host = os.getenv('AWS_DB_HOST', self.config.AWS_DB.AWS_DB_HOST)
        self.port = os.getenv('AWS_DB_PORT', self.config.AWS_DB.AWS_DB_PORT)
        self.database = os.getenv('AWS_DB_DATABASE', self.config.AWS_DB.AWS_DB_DATABASE)
        self.region = os.getenv('AWS_DB_REGION', self.config.AWS_DB.AWS_DB_REGION)
        self.use_iam_auth = use_iam_auth

        import pdb; pdb.set_trace()

        # Initialize boto3 for IAM authentication
        if use_iam_auth:
            self.rds_client = boto3.client(
                'rds',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', self.config.AWS.AWS_ACCESS_KEY_ID),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', self.config.AWS.AWS_SECRET_ACCESS_KEY),
                region_name=self.region
            )

        # SSL parameters for secure connection
        # self.ssl_params = {
        #     'sslmode': 'require',
        #     'sslcert': '/path/to/rds-ca-2019-root.pem'  # Path to RDS SSL certificate (download from AWS)
        # }

        self.ssl_params = {}

    def _generate_iam_token(self):
        """
        Generate an IAM authentication token for RDS.

        Returns:
            str: Temporary authentication token.
        """
        try:
            token = self.rds_client.generate_db_auth_token(
                DBHostname=self.host,
                Port=self.port,
                DBUsername=self.username,
                Region=self.region
            )
            return token
        except ClientError as e:
            raise Exception(f"Failed to generate IAM auth token: {str(e)}")

    def _create_engine(self):
        """
        Create SQLAlchemy engine based on authentication method.

        Returns:
            Engine: SQLAlchemy engine object.
        """
        try:
            import  pdb; pdb.set_trace()
            if self.use_iam_auth:
                password = self._generate_iam_token()
                connection_string = (
                    f"{self.db_type}://{self.username}:{password}@{self.host}:{self.port}/{self.database}"
                    # f"{self.db_type}://{self.username}:{password}@{self.host}:{self.port}/{self.database}"
                )
            else:
                connection_string = (
                    f"{self.db_type}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
                )
            # Add SSL parameters for secure connection
            if self.db_type in ['postgresql+psycopg2', 'mysql+pymysql']:
                connection_string += '?' + '&'.join(f"{key}={value}" for key, value in self.ssl_params.items())
            return create_engine(connection_string)
        except SQLAlchemyError as e:
            raise Exception(f"Failed to create SQLAlchemy engine: {str(e)}")

    def connect(self):
        """
        Establish the connection to the database using SQLAlchemy.
        """
        try:
            import pdb; pdb.set_trace()
            self.engine = self._create_engine()
            self.Session = sessionmaker(bind=self.engine)
            print("Database connection established.")
        except SQLAlchemyError as e:
            print(f"Error connecting to the database: {e}")
            raise

    def get_session(self):
        """
        Get a.py new session from the sessionmaker.

        Returns:
            Session: A SQLAlchemy session.
        """
        if not self.Session:
            self.connect()
        return self.Session()

    def close_connection(self):
        """
        Close the database connection.
        """
        if self.engine:
            self.engine.dispose()
            print("Database connection closed.")


# Usage Example
if __name__ == "__main__":

    db_connection = DBConnection(use_iam_auth=True)  # Set to True for IAM auth
    db_connection.connect()

    # Get a.py session and perform database operations
    session = db_connection.get_session()
    try:
        # Example query (assuming a.py table like 'files' exists)
        result = session.execute("SELECT * FROM files").fetchall()
        print(f"Result: {result}")
    except SQLAlchemyError as e:
        print(f"Error during database operation: {e}")
    finally:
        session.close()
        db_connection.close_connection()
