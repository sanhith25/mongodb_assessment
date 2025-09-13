from pydantic import BaseModel, Field
from typing import Optional

class EmployeeBase(BaseModel):
    employee_id: str = Field(..., example="EMP001", description="Unique employee identifier")
    name: str = Field(..., example="John Doe")
    age: int = Field(..., ge=18, le=100, example=30)
    department: str = Field(..., example="Engineering")
    salary: float = Field(..., ge=0, example=50000.0)

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=18, le=100)
    department: Optional[str] = None
    salary: Optional[float] = Field(None, ge=0)

class EmployeeOut(EmployeeBase):
    id: str = Field(..., example="64f3b2c0a7d9b1001f3c4e1a")
