from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import ProductionRun, Material, Machine, Operator


router = APIRouter(
    prefix="/impact",
    tags=["Impact Analysis"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{run_id}")
def get_production_impact(
    run_id: str,
    db: Session = Depends(get_db)
):

    run = db.query(ProductionRun).filter(
        ProductionRun.run_id == run_id
    ).first()

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Production run not found"
        )

    material = db.query(Material).filter(
        Material.material_id == run.material_id
    ).first()

    machine = db.query(Machine).filter(
        Machine.machine_id == run.machine_id
    ).first()

    operator = db.query(Operator).filter(
        Operator.operator_id == run.operator_id
    ).first()

    return {
        "run_id": run.run_id,
        "work_order": run.work_order,
        "product": run.product,
        "run_status": run.status,

        "material": {
            "material_id": run.material_id,
            "batch_id": material.batch_id if material else None,
            "status": material.status if material else "NOT_FOUND"
        },

        "machine": {
            "machine_id": run.machine_id,
            "status": machine.status if machine else "NOT_FOUND"
        },

        "operator": {
            "operator_id": run.operator_id,
            "status": operator.status if operator else "NOT_FOUND"
        }
    }