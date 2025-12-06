from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import func
from sqlalchemy.orm import Session

from models.simulation_like import Simulation
from models.simulation import SimulationLike
from models.user import User
from schemas.simulation import simulationResiter, simulation
from utils.dependencies import get_db
from utils.security import ALGORITHM, SECRET_KEY, get_current_user

router = APIRouter()

optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def _serialize_simulation(sim: Simulation, like_count: Optional[int] = None) -> dict:
    return {
        "id": sim.id,
        "title": sim.title,
        "data": sim.data,
        "data2": sim.data2,
        "is_public": sim.is_public,
        "owner_id": sim.owner_id,
        "created_at": sim.created_at,
        "updated_at": sim.updated_at,
        "likes": like_count if like_count is not None else len(sim.likes),
    }


def get_optional_user(
    db: Session = Depends(get_db), token: Optional[str] = Depends(optional_oauth2_scheme)
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    return db.query(User).filter(User.id == int(user_id)).first()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_simulation(
    sim_in: simulationResiter,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sim = Simulation(
        title=sim_in.title,
        data=sim_in.data,
        data2=sim_in.data2,
        is_public=sim_in.is_public,
        owner_id=current_user.id,
    )
    db.add(sim)
    db.commit()
    db.refresh(sim)
    return {"simulationId": sim.id}


@router.get("/")
def list_simulations(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort: str = Query("latest", pattern="^(latest|likes)$"),
) -> List[dict]:
    offset = (page - 1) * size
    if sort == "likes":
        query = (
            db.query(Simulation, func.count(SimulationLike.id).label("like_count"))
            .outerjoin(SimulationLike, Simulation.id == SimulationLike.simulation_id)
            .filter(Simulation.is_public.is_(True))
            .group_by(Simulation.id)
            .order_by(func.count(SimulationLike.id).desc(), Simulation.created_at.desc())
        )
        rows = query.offset(offset).limit(size).all()
        return [
            _serialize_simulation(sim, like_count=like_count) for sim, like_count in rows
        ]

    sims = (
        db.query(Simulation)
        .filter(Simulation.is_public.is_(True))
        .order_by(Simulation.created_at.desc())
        .offset(offset)
        .limit(size)
        .all()
    )
    return [_serialize_simulation(sim) for sim in sims]


@router.get("/{simulation_id}")
def get_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not sim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="시뮬레이션을 찾을 수 없습니다.")
    if not sim.is_public and (not current_user or current_user.id != sim.owner_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="비공개 시뮬레이션입니다.")
    return _serialize_simulation(sim)


@router.patch("/{simulation_id}")
def update_simulation(
    simulation_id: int,
    sim_in: simulation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not sim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="시뮬레이션을 찾을 수 없습니다.")
    if sim.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="수정 권한이 없습니다.")

    sim.title = sim_in.title
    db.add(sim)
    db.commit()
    db.refresh(sim)
    return _serialize_simulation(sim)


@router.post("/{simulation_id}/like")
def like_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not sim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="시뮬레이션을 찾을 수 없습니다.")

    existing = (
        db.query(SimulationLike)
        .filter(
            SimulationLike.simulation_id == simulation_id,
            SimulationLike.user_id == current_user.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 좋아요를 눌렀습니다.")

    like = SimulationLike(user_id=current_user.id, simulation_id=simulation_id)
    db.add(like)
    db.commit()

    like_count = (
        db.query(SimulationLike).filter(SimulationLike.simulation_id == simulation_id).count()
    )
    return {"simulationId": simulation_id, "likes": like_count}


@router.delete("/{simulation_id}/like")
def unlike_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    like = (
        db.query(SimulationLike)
        .filter(
            SimulationLike.simulation_id == simulation_id,
            SimulationLike.user_id == current_user.id,
        )
        .first()
    )
    if not like:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="좋아요한 기록이 없습니다.")

    db.delete(like)
    db.commit()

    like_count = (
        db.query(SimulationLike).filter(SimulationLike.simulation_id == simulation_id).count()
    )
    return {"simulationId": simulation_id, "likes": like_count}
