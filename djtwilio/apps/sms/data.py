from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Binary, Integer

Base = declarative_base()


class CtcBlob(Base):
    __tablename__ = 'ctc_blob'

    bctc_no = Column(Integer, primary_key=True, autoincrement=True)
    txt = Column(Binary)

    def __repr__(self):
        return str(self.txt)
