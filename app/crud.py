# app/crud.py
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException
from .db import employees_collection

def _convert_joining_date(value: Any) -> Optional[date]:
    """Convert possible Mongo/stored joining_date to a date object or None."""
    if value is None:
        return None
    # If stored as datetime (Mongo ISODate) -> convert to date
    if isinstance(value, datetime):
        return value.date()
    # If stored as date (unlikely from Mongo, but safe)
    if isinstance(value, date):
        return value
    # If stored as string "YYYY-MM-DD", try parse
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            # try other common ISO variants
            try:
                return datetime.fromisoformat(value).date()
            except Exception:
                return None
    return None

def _doc_to_employee(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB document to API-friendly dict."""
    return {
        "id": str(doc.get("_id")),
        "employee_id": doc.get("employee_id"),
        "name": doc.get("name"),
        "age": doc.get("age"),
        "department": doc.get("department"),
        "salary": doc.get("salary"),
        "joining_date": _convert_joining_date(doc.get("joining_date")),
        "skills": doc.get("skills", []),
    }

# ---------- CRUD: 4 core operations ----------

async def create_employee(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new employee; raise 400 if employee_id duplicate."""
    try:
        res = await employees_collection.insert_one(data)
        doc = await employees_collection.find_one({"_id": res.inserted_id})
        return _doc_to_employee(doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="employee_id already exists")

async def get_employee_by_employee_id(employee_id: str) -> Optional[Dict[str, Any]]:
    doc = await employees_collection.find_one({"employee_id": employee_id})
    if not doc:
        return None
    return _doc_to_employee(doc)

async def update_employee(employee_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    res = await employees_collection.update_one({"employee_id": employee_id}, {"$set": update_data})
    if res.matched_count == 0:
        return None
    doc = await employees_collection.find_one({"employee_id": employee_id})
    return _doc_to_employee(doc)

async def delete_employee(employee_id: str) -> int:
    res = await employees_collection.delete_one({"employee_id": employee_id})
    return res.deleted_count

# ---------- Aggregation / Query helpers ----------

async def list_employees_by_department(department: str) -> List[Dict[str, Any]]:
    """
    Return employees for a department sorted by joining_date (newest first).
    Note: if joining_date missing on some docs they will come last.
    """
    # sort -1 for newest first; nulls come last
    cursor = employees_collection.find({"department": department}).sort("joining_date", -1)
    docs = await cursor.to_list(length=None)
    return [_doc_to_employee(d) for d in docs]

async def average_salary_by_department() -> List[Dict[str, Any]]:
    """
    Aggregation pipeline to compute average salary per department.
    Output format: [{ "department": "Engineering", "avg_salary": 80000.0 }, ...]
    """
    pipeline = [
        {"$group": {"_id": "$department", "avg_salary": {"$avg": "$salary"}}},
        {"$project": {"_id": 0, "department": "$_id", "avg_salary": {"$round": ["$avg_salary", 2]}}}
    ]
    cursor = employees_collection.aggregate(pipeline)
    result = []
    async for doc in cursor:
        result.append(doc)
    return result

async def search_employees_by_skill(skill: str) -> List[Dict[str, Any]]:
    """Return employees who have `skill` inside their skills array."""
    cursor = employees_collection.find({"skills": skill})
    docs = await cursor.to_list(length=None)
    return [_doc_to_employee(d) for d in docs]
