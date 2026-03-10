import os
import uuid
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Table,
    Float,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

load_dotenv()

# ---------------------------------------------------
# Database URL handling (prefixes, SSL, etc.)
# ---------------------------------------------------
raw_url = os.getenv("DATABASE_URL", os.getenv("POSTGRES_URL", "sqlite:///./app.db"))
if raw_url.startswith("postgresql+asyncpg://"):
    raw_url = raw_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
elif raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql+psycopg://")

connect_args = {}
if raw_url.startswith("postgresql+psycopg://") and "localhost" not in raw_url:
    connect_args["sslmode"] = "require"

engine = create_engine(raw_url, connect_args=connect_args, future=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()
TABLE_PREFIX = "ls_"

# ---------------------------------------------------
# Association table for many‑to‑many Bookmark ↔ Tag
# ---------------------------------------------------
bookmark_tag = Table(
    f"{TABLE_PREFIX}bookmark_tag",
    Base.metadata,
    Column("bookmark_id", String, ForeignKey(f"{TABLE_PREFIX}bookmarks.id"), primary_key=True),
    Column("tag_id", String, ForeignKey(f"{TABLE_PREFIX}tags.id"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

# ---------------------------------------------------
# Core models
# ---------------------------------------------------
class User(Base):
    __tablename__ = f"{TABLE_PREFIX}users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True))

    bookmarks = relationship("Bookmark", back_populates="user")
    summaries = relationship("Summary", back_populates="user")
    tags = relationship("Tag", back_populates="user")

class Bookmark(Base):
    __tablename__ = f"{TABLE_PREFIX}bookmarks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey(f"{TABLE_PREFIX}users.id"), nullable=False)
    url = Column(String(2048), nullable=False)
    title = Column(String(255))
    is_favorite = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="bookmarks")
    summary = relationship("Summary", uselist=False, back_populates="bookmark")
    tags = relationship("Tag", secondary=bookmark_tag, back_populates="bookmarks")

class Summary(Base):
    __tablename__ = f"{TABLE_PREFIX}summaries"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bookmark_id = Column(String, ForeignKey(f"{TABLE_PREFIX}bookmarks.id"), nullable=False, unique=True)
    user_id = Column(String, ForeignKey(f"{TABLE_PREFIX}users.id"), nullable=False)
    summary = Column(Text, nullable=False)
    ai_model = Column(String(50), nullable=False)
    confidence_score = Column(Float)
    is_edited = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    bookmark = relationship("Bookmark", back_populates="summary")
    user = relationship("User", back_populates="summaries")

class Tag(Base):
    __tablename__ = f"{TABLE_PREFIX}tags"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey(f"{TABLE_PREFIX}users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    parent_tag_id = Column(String, ForeignKey(f"{TABLE_PREFIX}tags.id"))
    color = Column(String(7))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="tags")
    parent = relationship("Tag", remote_side=[id])
    bookmarks = relationship("Bookmark", secondary=bookmark_tag, back_populates="tags")

# Create tables if they do not exist
Base.metadata.create_all(bind=engine)