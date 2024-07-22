from sqlalchemy import BigInteger, Column, Index, String, TIMESTAMP
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Event(Base):
    __tablename__ = 'event'
    github_id = Column(BigInteger, primary_key=True, nullable=False)
    type = Column(String(32), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    repo = Column(String(255), nullable=False)

    __table_args__ = (
        Index('idx_created_at', 'created_at'),
    )
