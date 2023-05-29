from sqlalchemy import Column, Integer, String, Date
from ..database import Base

class Social(Base):
    __tablename__ = 'socials'

    id = Column(Integer, primary_key=True)
    wallet_address = Column(String, nullable=False)
    social_type = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    date_joined = Column(Date, nullable=False)

    def __init__(self):
        pass