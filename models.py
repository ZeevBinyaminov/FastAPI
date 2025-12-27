from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime, UTC

Base = declarative_base()


class RequestHistory(Base):
    """Model for storing request history"""
    __tablename__ = "request_history"

    id = Column(Integer, primary_key=True, index=True)
    smart_contract_address = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    request_headers = Column(JSON, nullable=True)
    response_status = Column(String, nullable=True)
    response_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.now(UTC), nullable=False)
