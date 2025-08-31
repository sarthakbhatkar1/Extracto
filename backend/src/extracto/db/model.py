from sqlalchemy import Column, String, DateTime, create_engine, TEXT, MetaData, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

from extracto.db.azure.base import DBConnection
from extracto.db.util import get_db_schema

metadata = MetaData(schema=get_db_schema())
Base = declarative_base(metadata=metadata)


class User(Base):
    __tablename__ = "USER"
    ID = Column(String(37), primary_key=True)
    NAME = Column(String(4096), nullable=False)
    SURNAME = Column(String(4096), nullable=False)
    ROLE = Column(TEXT)
    CREATED_TS = Column(DateTime(timezone=True))
    MODIFIED_TS = Column(DateTime(timezone=True))


class Project(Base):
    __tablename__ = "PROJECT"
    ID = Column(String(37), primary_key=True)
    NAME = Column(String(4096), nullable=False)
    TAGS = Column(JSONB, default=[])
    WORKFLOW = Column(JSONB, default={})
    DESCRIPTION = Column(TEXT)
    OWNER = Column(String(37), ForeignKey("USER.ID"), nullable=False)
    CREATED_TS = Column(DateTime(timezone=True))
    MODIFIED_TS = Column(DateTime(timezone=True))


class Document(Base):
    __tablename__ = 'DOCUMENT'
    ID = Column(String(37), primary_key=True)
    NAME = Column(String(4096), nullable=False)
    TYPE = Column(String(4096), unique=True, nullable=False)
    PROJECT_ID = Column(String(37), ForeignKey("PROJECT.ID"), nullable=False)
    FOLDER_NAME = Column(String(4096))
    STORAGE_PATH = Column(JSONB, default={})
    CREATED_BY = Column(TEXT)
    MODIFIED_BY = Column(TEXT)
    CREATED_TS = Column(DateTime(timezone=True))
    MODIFIED_TS = Column(DateTime(timezone=True))


class Task(Base):
    __tablename__ = 'TASK'
    ID = Column(String(37), primary_key=True)
    DOCUMENT_IDS = Column(JSONB, default=[])
    AI_RESULT = Column(JSONB, default={})
    OUTPUT = Column(JSONB, default={})
    CREATED_BY = Column(TEXT)
    MODIFIED_BY = Column(TEXT)
    CREATED_TS = Column(DateTime(timezone=True))
    MODIFIED_TS = Column(DateTime(timezone=True))


class WorkflowConfig(Base):
    __tablename__ = "WORKFLOW_CONFIG"
    ID = Column(String(37), primary_key=True)
    NAME = Column(String(4096), nullable=False)
    WORKFLOW = Column(JSONB, default={})
    DESCRIPTION = Column(TEXT)
    CREATED_BY = Column(TEXT)
    MODIFIED_BY = Column(TEXT)
    CREATED_TS = Column(DateTime(timezone=True))
    MODIFIED_TS = Column(DateTime(timezone=True))


# Database Setup
def setup_database(connection_string):
    """
    Creates the database tables based on the defined ORM models.

    :param connection_string: SQLAlchemy's connection string.
    """
    engine = create_engine(connection_string, echo=True)  # Set echo=True to see SQL logs
    Base.metadata.create_all(engine)
    return engine


# Usage Example
# if __name__ == "__main__":
#     connection_string = "sqlite:///example.db"  # Example with SQLite; replace with your DB URI
#     engine = setup_database(connection_string)
#
#     # Create a.py session
#     Session = sessionmaker(bind=engine)
#     session = Session()
#
#     # db_connection = DBConnection(**db_config)
#
#     Base.metadata.create_all(engine)

# Usage Example
if __name__ == "__main__":
    # To re-create database
    db_connection = DBConnection()
    engine = db_connection._create_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # DB Connection
    db_connection.connect()
    # Get a.py session and perform database operations
    session = db_connection.get_session()
    try:
        # Example: Querying data
        result = session.query(Project).all()
        print(f"result: {result}")
    except Exception as e:
        print(f"Error during database operation: {e}")
    finally:
        session.close()
        db_connection.close_connection()
    print(f"Database created successfully.")
    pass
