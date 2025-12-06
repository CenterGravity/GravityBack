from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class SimulationLike(Base):
    __tablename__ = "simulation_likes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # 누가 / 어떤 시뮬레이션에 좋아요 했는지
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # 한 유저가 한 시뮬레이션에 여러 번 좋아요 못 누르게
    __table_args__ = (
        UniqueConstraint("user_id", "simulation_id", name="uq_user_simulation_like"),
    )

    user = relationship("User", back_populates="likes")
    simulation = relationship("Simulation", back_populates="likes")
