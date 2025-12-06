# app/models/user.py

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from database import Base  # 경로는 프로젝트 구조에 맞게 조정


class User(Base):
    __tablename__ = "users"

    # 기본 PK
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # DTO: UserCreate.username
    username = Column(String(50), nullable=False)

    # DTO: UserCreate.email
    email = Column(String(255), nullable=False, unique=True, index=True)

    # 비밀번호(나중에 auth에서 사용할 가능성 높아서 미리 만들어 둠)
    hashed_password = Column(String(255), nullable=True)

    # DTO: UserCreate.created_at
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    # 관계 설정 (옵션)
    articles = relationship("Article", back_populates="author", cascade="all, delete-orphan")
    simulations = relationship("Simulation", back_populates="owner", cascade="all, delete-orphan")
    likes = relationship("SimulationLike", back_populates="user", cascade="all, delete-orphan")
