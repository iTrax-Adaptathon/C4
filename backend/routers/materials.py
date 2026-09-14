from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Material
from schemas import MaterialCreate, MaterialStatusUpdate


router = APIRouter(
    prefix="/materials",
    tags=["Materials"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_material(
    material: MaterialCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Material).filter(
        Material.material_id == material.material_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Material already exists"
        )

    new_material = Material(
        material_id=material.material_id,
        name=material.name,
        batch_id=material.batch_id,
        quantity=material.quantity,
        location=material.location,
        status=material.status
    )

    db.add(new_material)
    db.commit()
    db.refresh(new_material)

    return new_material


@router.get("/")
def get_materials(db: Session = Depends(get_db)):
    return db.query(Material).all()


@router.get("/{material_id}")
def get_material(
    material_id: str,
    db: Session = Depends(get_db)
):
    material = db.query(Material).filter(
        Material.material_id == material_id
    ).first()

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    return material


@router.patch("/{material_id}/status")
def update_material_status(
    material_id: str,
    status_update: MaterialStatusUpdate,
    db: Session = Depends(get_db)
):
    material = db.query(Material).filter(
        Material.material_id == material_id
    ).first()

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    material.status = status_update.status

    db.commit()
    db.refresh(material)

    return {
        "message": "Material status updated",
        "material_id": material.material_id,
        "status": material.status
    }