from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from base import Base

class Section(Base):
    __tablename__ = 'sections'
    id = Column(Integer, primary_key=True)
    version_id = Column(Integer, ForeignKey('versions.id'))
    version = relationship("Version")
    name = Column(String)

    def __init__(self, name, version):
        self.name = name
        self.version = version