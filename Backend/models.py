from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime
)

from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    projects = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete"
    )

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    description = Column(Text, nullable=True)

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    owner = relationship(
        "User",
        back_populates="projects"
    )

    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete"
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)

    description = Column(Text, nullable=True)

    status = Column(
        String(50),
        default="Todo"
    )

    priority = Column(
        String(50),
        default="Medium"
    )

    due_date = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id")
    )

    project = relationship(
        "Project",
        back_populates="tasks"
    )