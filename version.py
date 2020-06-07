from sqlalchemy import Column, String, Integer, DateTime
from base import Base

class Version(Base):
    __tablename__ = 'versions'
    id = Column(Integer, primary_key=True)
    date = Column(String)

    def __init__(self, date):
        self.date = date