from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(String, unique=True, index=True)
    name = Column(String)
    batch_id = Column(String)
    quantity = Column(Float)
    location = Column(String)
    status = Column(String, default="AVAILABLE")


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, unique=True, index=True)
    name = Column(String)
    status = Column(String, default="AVAILABLE")
    current_run = Column(String, nullable=True)


class Operator(Base):
    __tablename__ = "operators"

    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(String, unique=True, index=True)
    name = Column(String)
    status = Column(String, default="AVAILABLE")
    shift = Column(String)


class ProductionRun(Base):
    __tablename__ = "production_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, index=True)
    work_order = Column(String)
    product = Column(String)
    quantity = Column(Float)
    due_date = Column(String)
    status = Column(String, default="PLANNED")

    material_id = Column(String)
    machine_id = Column(String)
    operator_id = Column(String)


class Traceability(Base):
    __tablename__ = "traceability"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String)
    material_id = Column(String)
    batch_id = Column(String)
    machine_id = Column(String)
    operator_id = Column(String)
    event_type = Column(String)
    description = Column(String)
    timestamp = Column(DateTime)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String)
    severity = Column(String)
    run_id = Column(String, nullable=True)
    resource_id = Column(String, nullable=True)
    message = Column(String)
    status = Column(String, default="ACTIVE")