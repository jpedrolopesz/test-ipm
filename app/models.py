from sqlalchemy import Column, Integer, String, BigInteger, Boolean
from app.config import Base

class MediaFile(Base):
    __tablename__ = 'media_files'

    file_id = Column(String(64), primary_key=True)
    file_name = Column(String(100), nullable=False)
    file_hash = Column(String(64))
    file_object_key = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=False)
    create_time = Column(BigInteger, nullable=False)
    update_time = Column(BigInteger, nullable=False)

    def __repr__(self):
        return '<MediaFile %r>' % (self.file_name)

class WaylineFile(Base):
    __tablename__ = 'wayline_file'

    wayline_id = Column(String(64), primary_key=True)
    wayline_name = Column(String(64), nullable=False, default='')
    wayline_hash = Column(String(64), nullable=False, default='')
    wayline_object_key = Column(String(200), nullable=False, default='')
    favorited = Column(Boolean, nullable=False, default=False)
    create_time = Column(BigInteger, nullable=False)
    update_time = Column(BigInteger, nullable=False)
