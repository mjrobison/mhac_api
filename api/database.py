from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager, contextmanager

from config import config
import os

config = config.get(os.environ.get('API_ENV', 'development'))
DATABASE_URL = config.DB_URL

engine = create_engine(
    DATABASE_URL, pool_size = 5
)
db = sessionmaker(autocommit=False, autoflush=True, bind=engine)

@contextmanager
def database_conn(*args, **kwargs):
    try:
        yield db
        db.commit()
    except:
        db.rollback()
    finally:
        db.close()
