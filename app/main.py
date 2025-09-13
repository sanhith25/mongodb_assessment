from fastapi import FastAPI
from .routers import employees as employees_router
from .db import db

app = FastAPI(title="Junior SDE - Employee API")

# Register routes
app.include_router(employees_router.router, prefix="/employees", tags=["employees"])

@app.get("/")
async def root():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    # Create unique index on employee_id to enforce uniqueness at DB level
    # Creating here ensures index exists when the app starts
    await db["employees"].create_index("employee_id", unique=True)

