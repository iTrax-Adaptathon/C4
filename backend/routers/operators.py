from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Operator
from schemas import OperatorCreate


router = APIRouter(
    prefix="/operators",
    tags=["Operators"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_operator(
    operator: OperatorCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Operator).filter(
        Operator.operator_id == operator.operator_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Operator already exists"
        )

    new_operator = Operator(
        operator_id=operator.operator_id,
        name=operator.name,
        status=operator.status,
        shift=operator.shift
    )

    db.add(new_operator)
    db.commit()
    db.refresh(new_operator)

    return new_operator


@router.get("/")
def get_operators(db: Session = Depends(get_db)):
    return db.query(Operator).all()


@router.get("/{operator_id}")
def get_operator(
    operator_id: str,
    db: Session = Depends(get_db)
):
    operator = db.query(Operator).filter(
        Operator.operator_id == operator_id
    ).first()

    if not operator:
        raise HTTPException(
            status_code=404,
            detail="Operator not found"
        )

    return operator


@router.patch("/{operator_id}/status")
def update_operator_status(
    operator_id: str,
    status: str,
    db: Session = Depends(get_db)
):
    operator = db.query(Operator).filter(
        Operator.operator_id == operator_id
    ).first()

    if not operator:
        raise HTTPException(
            status_code=404,
            detail="Operator not found"
        )

    operator.status = status

    db.commit()
    db.refresh(operator)

    return operator