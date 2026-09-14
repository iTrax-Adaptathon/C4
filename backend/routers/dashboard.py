from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import (
    Material,
    Machine,
    Operator,
    ProductionRun,
    Alert
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_dashboard(db: Session = Depends(get_db)):

    total_materials = db.query(Material).count()
    total_machines = db.query(Machine).count()
    total_operators = db.query(Operator).count()
    total_runs = db.query(ProductionRun).count()

    running_runs = db.query(ProductionRun).filter(
        ProductionRun.status == "RUNNING"
    ).count()

    planned_runs = db.query(ProductionRun).filter(
        ProductionRun.status == "PLANNED"
    ).count()

    active_alerts = db.query(Alert).filter(
        Alert.status == "ACTIVE"
    ).count()

    return {
        "materials": total_materials,
        "machines": total_machines,
        "operators": total_operators,
        "production_runs": total_runs,
        "running_runs": running_runs,
        "planned_runs": planned_runs,
        "active_alerts": active_alerts
    }