from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)


class ActiveSession(Base):
    __tablename__ = "active_session"

    id = Column(Integer, primary_key=True)

    category = Column(String)
    task = Column(String)

    start_time = Column(DateTime)

    is_running = Column(Boolean, default=True)


class SessionHistory(Base):
    __tablename__ = "session_history"

    id = Column(Integer, primary_key=True)

    category = Column(String)
    task = Column(String)

    start_time = Column(DateTime)
    end_time = Column(DateTime)

    duration = Column(Integer)

    session_date = Column(String)

    notes = Column(String)


class AppSettings(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True)

    daily_goal = Column(Integer, default=8)