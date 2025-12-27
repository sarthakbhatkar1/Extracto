import os
import uuid

from sqlalchemy import create_engine, MetaData, Column, String, DateTime, ForeignKey, Boolean, TEXT
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base, relationship

from extracto.db.azure.base import DBConnection
from extracto.db.util import get_db_schema

metadata = MetaData(schema=get_db_schema())
Base = declarative_base(metadata=metadata)


class User(Base):
    __tablename__ = "USER"

    ID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    FIRST_NAME = Column(String(4096), nullable=False)
    LAST_NAME = Column(String(4096), nullable=False)
    EMAIL = Column(String(4096))
    ROLE = Column(String(4096))
    HASHED_PASSWORD = Column(TEXT, nullable=False)
    IS_ACTIVE = Column(Boolean, nullable=False)
    IS_VERIFIED = Column(Boolean, nullable=False, default=False)
    CREATED_AT = Column(DateTime(timezone=True))
    MODIFIED_AT = Column(DateTime(timezone=True))

    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="owner_ref", cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = "REFRESH_TOKEN"

    ID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    USER_ID = Column(UUID(as_uuid=True), ForeignKey("USER.ID"), nullable=False)
    TOKEN_HASH = Column(String(4096), unique=True)
    REVOKED = Column(Boolean, default=False)
    EXPIRED_AT = Column(DateTime(timezone=True), nullable=True)
    CREATED_AT = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")


class Project(Base):
    __tablename__ = "PROJECT"

    ID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    NAME = Column(String(4096), nullable=False)
    TAGS = Column(JSONB, default=[])
    WORKFLOW = Column(JSONB, default={})
    DESCRIPTION = Column(TEXT)
    OWNER = Column(UUID(as_uuid=True), ForeignKey("USER.ID"), nullable=False)
    CREATED_AT = Column(DateTime(timezone=True))
    MODIFIED_AT = Column(DateTime(timezone=True))

    # Relationships
    owner_ref = relationship("User", back_populates="projects")
    documents = relationship("Document", back_populates="project_ref", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "DOCUMENT"

    ID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    NAME = Column(String(4096), nullable=False)
    TYPE = Column(String(4096), nullable=False)
    PROJECT_ID = Column(UUID(as_uuid=True), ForeignKey("PROJECT.ID"), nullable=False)
    FOLDER_NAME = Column(String(4096))
    STORAGE_PATH = Column(JSONB, default={})
    CREATED_AT = Column(DateTime(timezone=True))
    MODIFIED_AT = Column(DateTime(timezone=True))

    # Relationships
    project_ref = relationship("Project", back_populates="documents")


class Task(Base):
    __tablename__ = "TASK"

    ID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    DOCUMENT_IDS = Column(JSONB, default=[])
    STATUS = Column(JSONB, nullable=False)
    AI_RESULT = Column(JSONB, default={})
    OUTPUT = Column(JSONB, default={})
    CREATED_AT = Column(DateTime(timezone=True))
    MODIFIED_AT = Column(DateTime(timezone=True))


class WorkflowConfig(Base):
    __tablename__ = "WORKFLOW_CONFIG"

    ID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    NAME = Column(String(4096), nullable=False)
    WORKFLOW = Column(JSONB, default={})
    DESCRIPTION = Column(TEXT)
    CREATED_BY = Column(TEXT)
    MODIFIED_BY = Column(TEXT)
    CREATED_AT = Column(DateTime(timezone=True))
    MODIFIED_AT = Column(DateTime(timezone=True))


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
if __name__ == "__main__":
    # To re-create database
    os.getenv('CONF_PATH', r"D:\Projects\career\Extracto\backend\resource")
    os.getenv('ENV', "PREDEV")

    db_connection = DBConnection()
    engine = db_connection._create_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print(f"Database created successfully.")
    pass
