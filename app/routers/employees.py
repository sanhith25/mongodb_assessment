from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from ..schemas import EmployeeCreate, EmployeeUpdate, EmployeeOut
from .. import crud

router = APIRouter(prefix="/employees", tags=["employees"])

@router.post("/", response_model=EmployeeOut, status_code=201)
async def create_employee_endpoint(payload: EmployeeCreate):
    employee = payload.dict()
    created = await crud.create_employee(employee)
    return created

@router.get("/{employee_id}", response_model=EmployeeOut)
async def get_employee_endpoint(employee_id: str):
    doc = await crud.get_employee_by_employee_id(employee_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Employee not found")
    return doc

@router.put("/{employee_id}", response_model=EmployeeOut)
async def update_employee_endpoint(employee_id: str, payload: EmployeeUpdate):
    update_data = {k: v for k, v in payload.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")
    doc = await crud.update_employee(employee_id, update_data)
    if not doc:
        raise HTTPException(status_code=404, detail="Employee not found")
    return doc

@router.delete("/{employee_id}", status_code=204)
async def delete_employee_endpoint(employee_id: str):
    deleted = await crud.delete_employee(employee_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return None

@router.get("/by-department", response_model=List[EmployeeOut])
async def list_by_department(department: str = Query(..., description="Department name")):
    docs = await crud.list_employees_by_department(department)
    return docs

@router.get("/avg-salary")
async def avg_salary():
    """
    Returns average salary grouped by department using MongoDB aggregation.
    Example response:
    [{ "department": "Engineering", "avg_salary": 80000.0 }, ...]
    """
    result = await crud.average_salary_by_department()
    return result

@router.get("/search", response_model=List[EmployeeOut])
async def search_by_skill(skill: str = Query(..., description="Skill to search (exact match in skills array)")):
    docs = await crud.search_employees_by_skill(skill)
    return docs
