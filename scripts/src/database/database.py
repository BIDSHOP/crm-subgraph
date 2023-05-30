from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os
import sys

SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(str(SCRIPT_DIR.parent))

db_engine = create_engine(
    '',
    pool_pre_ping=True,
    pool_size=15,
    max_overflow=15
)

session_maker = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

Base = declarative_base()