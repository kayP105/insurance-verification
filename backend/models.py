from sqlalchemy import Column, Integer, String, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class User(Base):
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")  
    
class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    local_path = Column(String)
    status = Column(String, default="pending_ocr")
    extracted_json = Column(JSON, nullable=True)
    agent_notes = Column(String)
    agent_decision = Column(String)

class MockInsurerPolicy(Base):
    __tablename__ = "mock_insurer_db"
    id = Column(Integer, primary_key=True, index=True)
    policy_number = Column(String, unique=True, index=True)
    policy_holder_name = Column(String)
    coverage_type = Column(String)
    coverage_limit = Column(Integer)
    is_active = Column(Boolean, default=True)
