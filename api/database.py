from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import config
import os

config = config.get(os.environ.get('API_ENV', 'development'))
DATEBASE_URL = config.DB_URL

engine = create_engine(
    DATEBASE_URL, pool_size =2 
)
db = sessionmaker(autocommit=False, autoflush=True, bind=engine)

def get_db():
    return db()
