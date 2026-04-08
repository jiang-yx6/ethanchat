from functools import wraps
from contextlib import contextmanager
from sqlalchemy.orm import Session
from EthanChat.server.db.base import SessionLocal


@contextmanager
def session_get()->Session:
    """
    上下文管理器，获取session
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def with_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with session_get() as session:
            try:
                result = func(session, *args, **kwargs)
                session.commit()
                return result
            except:
                session.rollback()
                raise
    return wrapper

def get_db():
    db = SessionLocal()
    return db