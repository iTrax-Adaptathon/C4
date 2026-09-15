from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database import SessionLocal
from models import ProductionRun, Machine, Material, Operator, Traceability
from schemas import ProductionRunCreate


router = APIRouter(
    prefix="/production-runs",
    tags=["Production Runs"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_production_run(
    run: ProductionRunCreate,
    db: Session = Depends(get_db)
):

    # Check duplicate run
    existing = db.query(ProductionRun).filter(
        ProductionRun.run_id == run.run_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Production run already exists"
        )

    # Check machine double-booking
    machine_busy = db.query(ProductionRun).filter(
        ProductionRun.machine_id == run.machine_id,
        ProductionRun.status.in_(["PLANNED", "RUNNING"])
    ).first()

    if machine_busy:
        raise HTTPException(
            status_code=409,
            detail=f"Machine {run.machine_id} is already assigned to another production run"
        )

    # Check material double-booking
    material_busy = db.query(ProductionRun).filter(
        ProductionRun.material_id == run.material_id,
        ProductionRun.status.in_(["PLANNED", "RUNNING"])
    ).first()

    if material_busy:
        raise HTTPException(
            status_code=409,
            detail=f"Material {run.material_id} is already assigned to another production run"
        )

    # Create production run
    new_run = ProductionRun(
        run_id=run.run_id,
        work_order=run.work_order,
        product=run.product,
        quantity=run.quantity,
        due_date=run.due_date,
        status="PLANNED",
        material_id=run.material_id,
        machine_id=run.machine_id,
        operator_id=run.operator_id
    )

    db.add(new_run)
    db.commit()
    db.refresh(new_run)

    return new_run


@router.get("/")
def get_production_runs(db: Session = Depends(get_db)):
    return db.query(ProductionRun).all()


@router.get("/{run_id}")
def get_production_run(
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

    return run

@router.post("/{run_id}/start")
def start_production_run(
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

    if run.status != "PLANNED":
        raise HTTPException(
            status_code=400,
            detail="Production run cannot be started"
        )

    machine = db.query(Machine).filter(
        Machine.machine_id == run.machine_id
    ).first()

    material = db.query(Material).filter(
        Material.material_id == run.material_id
    ).first()

    operator = db.query(Operator).filter(
        Operator.operator_id == run.operator_id
    ).first()

    if not machine:
        raise HTTPException(
            status_code=404,
            detail="Machine not found"
        )

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    if not operator:
        raise HTTPException(
            status_code=404,
            detail="Operator not found"
        )

    if machine.status != "READY":
        raise HTTPException(
            status_code=409,
            detail="Machine is not ready"
        )

    if material.status != "AVAILABLE":
        raise HTTPException(
            status_code=409,
            detail="Material is not available"
        )

    if operator.status != "AVAILABLE":
        raise HTTPException(
            status_code=409,
            detail="Operator is not available"
        )

    # Start production run
    run.status = "RUNNING"

    # Update resource statuses
    machine.status = "RUNNING"
    machine.current_run = run.run_id

    material.status = "IN_USE"

    operator.status = "WORKING"

    trace_event = Traceability(
    run_id=run.run_id,
    material_id=material.material_id,
    batch_id=material.batch_id,
    machine_id=machine.machine_id,
    operator_id=operator.operator_id,
    event_type="RUN_STARTED",
    description=f"Production run {run.run_id} started",
    timestamp=datetime.now()
)

    db.add(trace_event)

    db.commit()
    db.refresh(run)

    return {
        "message": "Production run started successfully",
        "run_id": run.run_id,
        "run_status": run.status,
        "machine_status": machine.status,
        "material_status": material.status,
        "operator_status": operator.status
    }