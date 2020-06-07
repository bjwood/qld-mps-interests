from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from interest import Interest
from version import Version
from base import Base

class Member(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True)
    version_id = Column(Integer, ForeignKey('versions.id'))
    version = relationship("Version")
    first_name = Column(String)
    last_name = Column(String)
    electorate = Column(String)
    interests = relationship("Interest")

    def __init__(self, first_name, last_name, electorate, version):
        self.first_name = first_name
        self.last_name = last_name
        self.electorate = electorate
        self.version = version

    def add_interest(self, subsection, text):
        count = 0
        existing_index = -1
        for interest in self.interests:
            if interest.section == subsection:
                existing_index = count
                count += 1
        to_add = text.split("; ")
        for item in to_add:
            self.interests.append(Interest(self, subsection, item, self.version))
