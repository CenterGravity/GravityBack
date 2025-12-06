# app/models/simulation.py

from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Simulation(Base):
    __tablename__ = "simulations"

    # DTO: simulationResponse.simulationId
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # DTO: simulation.title
    title = Column(String(255), nullable=False)

    # DTO: simulationResiter.data, data2
    # 실제로는 float / json / text 등으로 바뀔 수도 있음
    data = Column(Integer, nullable=False)
    data2 = Column(Integer, nullable=False)

    # DTO: simulationResiter.is_public
    is_public = Column(Boolean, nullable=False, default=True)

    # 생성/수정 시간 (추가 필드)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # 어떤 유저의 시뮬레이션인지 (옵션)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    owner = relationship("User", back_populates="simulations")
    likes = relationship("SimulationLike", back_populates="simulation", cascade="all, delete-orphan")
