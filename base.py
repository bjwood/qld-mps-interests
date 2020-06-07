from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
import config

db_string = 'postgres://{0}:{1}@{2}/{3}'.format(
            config.DB_USER,
            config.DB_PASSWORD,
            config.DB_HOST,
            config.DB_NAME)
            
engine = create_engine(db_string)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
