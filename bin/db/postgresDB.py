from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy.orm import Session
from fastapi import Depends
from bin.config import settings

import logging

pg_database: Session = None
engine = create_engine(
    str(settings.PG_URL) ,
    future=True ,
    pool_size=50 ,
    max_overflow=10 ,
    pool_recycle=1800,
    connect_args={
        "keepalives": 1,
        "keepalives_idle": 60,  # seconds
        "keepalives_interval": 10,
        "keepalives_count": 5
    })
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)


# Log Configs
# dictConfig(logConfig.dict())
logger = logging.getLogger("device-manager")

def db_connection():
    """
    *Postgres database connection
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


Base = declarative_base()

pg_database: Session = Depends(db_connection())