from sqlalchemy import Column, String, DateTime, BigInteger
import datetime
from bot.sql_helper import Base, Session, engine
from cacheout import Cache

cache = Cache()


class RequestRecord(Base):
    __tablename__ = 'request_records'
    tg = Column(BigInteger, primary_key=True, autoincrement=False)
    download_id = Column(String, nullable=False)
    request_name = Column(String, nullable=False)
    create_at = Column(DateTime, default=datetime.datetime.utcnow)
    update_at = Column(DateTime, default=datetime.datetime.utcnow,
                       onupdate=datetime.datetime.utcnow)


RequestRecord.__table__.create(bind=engine, checkfirst=True)


def sql_add_request_record(tg: int, download_id: str, request_name: str):
    with Session() as session:
        try:
            request_record = RequestRecord(
                tg=tg, download_id=download_id, request_name=request_name)
            session.add(request_record)
            session.commit()
            return True
        except:
            session.rollback()
            return False


def sql_get_request_record(tg: int):
    with Session() as session:
        request_record = session.query(RequestRecord).filter(
            RequestRecord.tg == tg).all()
        return request_record


def sql_get_all_request_record():
    with Session() as session:
        request_record = session.query(RequestRecord).all()
        return request_record
