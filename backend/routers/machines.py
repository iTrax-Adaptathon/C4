from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Machine
from schemas import MachineCreate

router = APIRouter(
    prefix="/machines",
    tags=["Machines"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_machine(
    machine: MachineCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Machine).filter(
        Machine.machine_id == machine.machine_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Machine already exists"
        )

    new_machine = Machine(
        machine_id=machine.machine_id,
        name=machine.name,
        status=machine.status
    )

    db.add(new_machine)
    db.commit()
    db.refresh(new_machine)

    return new_machine


@router.get("/")
def get_machines(db: Session = Depends(get_db)):
    return db.query(Machine).all()


@router.get("/{machine_id}")
def get_machine(
    machine_id: str,
    db: Session = Depends(get_db)
):
    machine = db.query(Machine).filter(
        Machine.machine_id == machine_id
    ).first()

    if not machine:
        raise HTTPException(
            status_code=404,
            detail="Machine not found"
        )

    return machine


@router.patch("/{machine_id}/status")
def update_machine_status(
    machine_id: str,
    status: str,
    db: Session = Depends(get_db)
):
    machine = db.query(Machine).filter(
        Machine.machine_id == machine_id
    ).first()

    if not machine:
        raise HTTPException(
            status_code=404,
            detail="Machine not found"
        )

    machine.status = status

    db.commit()
    db.refresh(machine)

    return machine