from pydantic import BaseModel


class MaterialCreate(BaseModel):
    material_id: str
    name: str
    batch_id: str
    quantity: float
    location: str
    status: str = "AVAILABLE"


class MaterialStatusUpdate(BaseModel):
    status: str

class MachineCreate(BaseModel):
    machine_id: str
    name: str
    status: str = "READY"

class OperatorCreate(BaseModel):
    operator_id: str
    name: str
    status: str = "AVAILABLE"
    shift: str

class ProductionRunCreate(BaseModel):
    run_id: str
    work_order: str
    product: str
    quantity: float
    due_date: str
    material_id: str
    machine_id: str
    operator_id: str

class TraceabilityCreate(BaseModel):
    run_id: str
    event_type: str
    description: str