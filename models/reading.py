from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"))

    device = relationship("Device", back_populates="readings")
    recommendations = relationship("Recommendation", back_populates="reading")
