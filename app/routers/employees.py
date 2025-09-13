# app/routers/employees.py
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..schemas import EmployeeCreate, EmployeeUpdate, EmployeeOut
from .. import crud

router = APIRouter()

@router.post("/", response_model=EmployeeOut, status_code=201)
async def create_employee_endpoint(payload: EmployeeCreate):
    """Create a new employee."""
    employee = payload.dict()
    created = await crud.create_employee(employee)
    return created

@router.get("/", response_model=list[EmployeeOut])
async def list_employees_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search name (partial match)"),
    department: Optional[str] = Query(None, description="Filter by department"),
    min_salary: Optional[float] = Query(None, ge=0),
    max_salary: Optional[float] = Query(None, ge=0),
    sort_by: str = Query("employee_id", description="Field to sort by"),
    order: str = Query("asc", regex="^(asc|desc)$", description="Sort order: asc or desc")
):
    """List employees with optional search, filter, pagination and sort."""
    q = {}
    if search:
        q["name"] = {"$regex": search, "$options": "i"}
    if department:
        q["department"] = department
    if min_salary is not None or max_salary is not None:
        salary_q = {}
        if min_salary is not None:
            salary_q["$gte"] = min_salary
        if max_salary is not None:
            salary_q["$lte"] = max_salary
        q["salary"] = salary_q

    # Secure allowed sort fields
    allowed_sorts = {"employee_id", "name", "age", "salary", "department"}
    if sort_by not in allowed_sorts:
        raise HTTPException(status_code=400, detail=f"sort_by must be one of {allowed_sorts}")

    docs = await crud.list_employees(q, page, size, sort_by, order)
    return docs

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
