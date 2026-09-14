from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from database import SessionLocal
from models import Alert, ProductionRun, Material, Machine, Operator


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/check/{run_id}")
def check_production_run(
    run_id: str,
    db: Session = Depends(get_db)
):

    run = db.query(ProductionRun).filter(
        ProductionRun.run_id == run_id
    ).first()

    if not run:
        return {
            "message": "Production run not found"
        }

    alerts_created = []

    material = db.query(Material).filter(
        Material.material_id == run.material_id
    ).first()

    machine = db.query(Machine).filter(
        Machine.machine_id == run.machine_id
    ).first()

    operator = db.query(Operator).filter(
        Operator.operator_id == run.operator_id
    ).first()

    # Material problem
    if material and material.status == "ON_HOLD":

        alert = Alert(
            alert_type="MATERIAL_HOLD",
            severity="HIGH",
            run_id=run.run_id,
            resource_id=material.material_id,
            message=f"Material {material.material_id} is on hold",
            status="ACTIVE"
        )

        db.add(alert)

        alerts_created.append(
            f"Material {material.material_id} is on hold"
        )

    # Machine problem
    if machine and machine.status not in ["READY", "RUNNING"]:

        alert = Alert(
            alert_type="MACHINE_STATUS",
            severity="HIGH",
            run_id=run.run_id,
            resource_id=machine.machine_id,
            message=f"Machine {machine.machine_id} is not ready",
            status="ACTIVE"
        )

        db.add(alert)

        alerts_created.append(
            f"Machine {machine.machine_id} is not ready"
        )

    # Operator problem
    if operator and operator.status not in ["AVAILABLE", "WORKING"]:

        alert = Alert(
            alert_type="OPERATOR_STATUS",
            severity="MEDIUM",
            run_id=run.run_id,
            resource_id=operator.operator_id,
            message=f"Operator {operator.operator_id} is not available",
            status="ACTIVE"
        )

        db.add(alert)

        alerts_created.append(
            f"Operator {operator.operator_id} is not available"
        )

    db.commit()

    return {
        "run_id": run.run_id,
        "alerts_created": alerts_created,
        "checked_at": datetime.now()
    }


@router.get("/")
def get_alerts(db: Session = Depends(get_db)):
    return db.query(Alert).all()