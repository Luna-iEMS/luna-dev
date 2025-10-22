from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)
    reading_id = Column(Integer, ForeignKey("readings.id"))
    recommendation_text = Column(String, nullable=False)
    created_at = Column(DateTime)

    reading = relationship("Reading", back_populates="recommendations")
