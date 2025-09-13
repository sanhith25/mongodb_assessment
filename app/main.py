from fastapi import FastAPI
from .routers import employees as employees_router
from .db import db

app = FastAPI(title="Junior SDE - Employee API (CRUD + Aggregations)")

app.include_router(employees_router.router)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Employee API running"}

@app.on_event("startup")
async def startup_event():
    await db["employees"].create_index("employee_id", unique=True)
