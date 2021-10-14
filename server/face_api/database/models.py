from sqlalchemy import Column, VARCHAR, LargeBinary, Integer
from face_api.database.database import Base


class User(Base):
    __tablename__ = 'faces'

    id = Column(Integer, autoincrement=True, primary_key=True)
    first_name = Column(VARCHAR(50), index=True)
    last_name = Column(VARCHAR(50), index=True)
    alhosn_status = Column(VARCHAR(255), index=True)
    face_encoding = Column(LargeBinary)
