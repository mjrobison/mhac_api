from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from config import config
import os

config = config.get(os.environ.get('API_ENV', 'development'))
DATEBASE_URL = config.DB_URL

engine = create_engine(
    DATEBASE_URL, pool_size = 5
)
db = sessionmaker(autocommit=False, autoflush=True, bind=engine)

async def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def database_conn():
    DB = db()
    try:
        yield DB
        db.commit()
    except:
        DB.rollback()
    finally:
        DB.close()
