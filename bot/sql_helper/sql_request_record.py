from sqlalchemy import Column, String, DateTime, BigInteger, Text
import datetime
from bot.sql_helper import Base, Session, engine
from cacheout import Cache

cache = Cache()


class RequestRecord(Base):
    __tablename__ = 'request_records'
    download_id = Column(String(255), primary_key=True, autoincrement=False)
    tg = Column(BigInteger, nullable=False)
    request_name = Column(String(255), nullable=False)
    cost = Column(String(255), nullable=False)
    detail = Column(Text, nullable=False)
    create_at = Column(DateTime, default=datetime.datetime.utcnow)
    update_at = Column(DateTime, default=datetime.datetime.utcnow,
                       onupdate=datetime.datetime.utcnow)


RequestRecord.__table__.create(bind=engine, checkfirst=True)


def sql_add_request_record(tg: int, download_id: str, request_name: str, detail: str, cost: str):
    with Session() as session:
        try:
            request_record = RequestRecord(
                tg=tg, download_id=download_id, request_name=request_name, detail=detail, cost=cost)
            session.add(request_record)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False


def sql_get_request_record(tg: int, page: int = 1, limit: int = 5):
    with Session() as session:
        request_record = session.query(RequestRecord).filter(
            RequestRecord.tg == tg).limit(limit + 1).offset((page - 1) * limit).all()
        if len(request_record) == 0:
            return None, False, False
        if len(request_record) == limit + 1:
            has_next = True
            request_record = request_record[:-1]
        else:
            has_next = False
        if page > 1:
            has_prev = True
        else:
            has_prev = False
        return request_record, has_prev, has_next


def sql_get_all_request_record():
    with Session() as session:
        request_record = session.query(RequestRecord).all()
        return request_record
