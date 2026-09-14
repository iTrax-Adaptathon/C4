from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from schemas import TraceabilityCreate

from database import SessionLocal
from models import Traceability, ProductionRun, Material


router = APIRouter(
    prefix="/traceability",
    tags=["Traceability"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_traceability(
    data: TraceabilityCreate,
    db: Session = Depends(get_db)
):

    run = db.query(ProductionRun).filter(
        ProductionRun.run_id == data.run_id
    ).first()

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Production run not found"
        )

    material = db.query(Material).filter(
        Material.material_id == run.material_id
    ).first()

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    event = Traceability(
        run_id=run.run_id,
        material_id=run.material_id,
        batch_id=material.batch_id,
        machine_id=run.machine_id,
        operator_id=run.operator_id,
        event_type=data.event_type,
        description=data.description,
        timestamp=datetime.now()
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@router.get("/{run_id}")
def get_traceability(
    run_id: str,
    db: Session = Depends(get_db)
):

    events = db.query(Traceability).filter(
        Traceability.run_id == run_id
    ).all()

    if not events:
        raise HTTPException(
            status_code=404,
            detail="No traceability events found"
        )

    return events