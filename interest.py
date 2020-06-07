from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from base import Base

class Interest(Base):
    __tablename__ = 'interests'
    id = Column(Integer, primary_key=True)
    version_id = Column(Integer, ForeignKey('versions.id'))
    version = relationship("Version")
    member_id = Column(Integer, ForeignKey('members.id'))
    section_id = Column(Integer, ForeignKey('sections.id'))
    section = relationship("Section", backref="interests")
    text = Column(String)

    def __init__(self, member, section, text, version):
        self.member = member
        self.section = section
        self.text = text
        self.version = version