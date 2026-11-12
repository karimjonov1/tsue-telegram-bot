from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    BigInteger, Integer, String, Boolean, DateTime,
    ForeignKey, Text, UniqueConstraint, Index
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Faculty(Base):
    __tablename__ = "faculties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    groups: Mapped[List["Group"]] = relationship("Group", back_populates="faculty")


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    faculty_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("faculties.id"), nullable=True)
    course_year: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    faculty: Mapped[Optional["Faculty"]] = relationship("Faculty", back_populates="groups")
    lessons: Mapped[List["Lesson"]] = relationship("Lesson", back_populates="group", cascade="all, delete-orphan")
    users: Mapped[List["User"]] = relationship("User", back_populates="selected_group")
    chat_links: Mapped[List["ChatLink"]] = relationship("ChatLink", back_populates="group")


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    lessons: Mapped[List["Lesson"]] = relationship("Lesson", back_populates="teacher")


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    building: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    lessons: Mapped[List["Lesson"]] = relationship("Lesson", back_populates="room")


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)

    lessons: Mapped[List["Lesson"]] = relationship("Lesson", back_populates="subject")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("groups.id"), index=True, nullable=False)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("teachers.id"), nullable=True)
    room_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("rooms.id"), nullable=True)

    weekday: Mapped[int] = mapped_column(Integer, nullable=False)  # 1=Monday ... 6=Saturday
    slot_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 8
    start_time: Mapped[str] = mapped_column(String(10), nullable=False)  # e.g. "13:00"
    end_time: Mapped[str] = mapped_column(String(10), nullable=False)    # e.g. "14:20"
    lesson_type: Mapped[str] = mapped_column(String(20), default="Ma")   # Ma (Ma'ruza), Sem (Seminar), Lab, Sport
    week_type: Mapped[str] = mapped_column(String(20), default="EVERY")  # EVERY, WEEK_A, WEEK_B

    group: Mapped["Group"] = relationship("Group", back_populates="lessons")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="lessons")
    teacher: Mapped[Optional["Teacher"]] = relationship("Teacher", back_populates="lessons")
    room: Mapped[Optional["Room"]] = relationship("Room", back_populates="lessons")

    __table_args__ = (
        Index("idx_lesson_group_day_slot", "group_id", "weekday", "slot_number", "week_type"),
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user ID
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False, default="")
    selected_group_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("groups.id"), nullable=True)
    reminders_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    reminder_lead_minutes: Mapped[int] = mapped_column(Integer, default=10)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    selected_group: Mapped[Optional["Group"]] = relationship("Group", back_populates="users")


class ChatLink(Base):
    __tablename__ = "chat_links"

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram supergroup/group ID
    title: Mapped[str] = mapped_column(String(200), default="")
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("groups.id"), nullable=False)
    auto_post_time: Mapped[str] = mapped_column(String(10), default="07:00")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    linked_by: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    group: Mapped["Group"] = relationship("Group", back_populates="chat_links")


class SentReminder(Base):
    __tablename__ = "sent_reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    lesson_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    reminder_date: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", "reminder_date", name="uq_user_lesson_date"),
    )


class ChangeLog(Base):
    __tablename__ = "change_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    change_type: Mapped[str] = mapped_column(String(30), nullable=False)  # ADDED, REMOVED, MODIFIED
    details: Mapped[str] = mapped_column(Text, nullable=False)  # JSON or text diff description
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
