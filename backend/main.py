from fastapi import FastAPI


from database import engine, Base
import models
from routers.materials import router as material_router
from routers.machines import router as machine_router
from routers.operators import router as operator_router
from routers.production_runs import router as production_run_router
from routers.traceability import router as traceability_router
from routers.alerts import router as alert_router
from routers.impact import router as impact_router
from routers.dashboard import router as dashboard_router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Smart Manufacturing & Production Control Platform"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(material_router)
app.include_router(machine_router)
app.include_router(operator_router)
app.include_router(production_run_router)
app.include_router(traceability_router)
app.include_router(alert_router)
app.include_router(impact_router)
app.include_router(dashboard_router)



@app.get("/")
def home():
    return {
        "message": "Smart Manufacturing & Production Control Platform Backend is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

