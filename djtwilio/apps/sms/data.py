# -*- coding: utf-8 -*-

from sqlalchemy import Binary
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class CtcBlob(Base):
    """Data model class for the blob table."""

    __tablename__ = 'ctc_blob'

    bctc_no = Column(Integer, primary_key=True, autoincrement=True)
    txt = Column(Binary)

    def __repr__(self):
        """Default display value."""
        return str(self.txt)
