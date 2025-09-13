from typing import List, Optional, Dict, Any
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException
from .db import employees_collection

def _doc_to_employee(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB document to JSON-serializable dict for API response."""
    return {
        "id": str(doc["_id"]),
        "employee_id": doc["employee_id"],
        "name": doc["name"],
        "age": doc["age"],
        "department": doc["department"],
        "salary": doc["salary"],
    }

async def create_employee(data: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a new employee document. Raises HTTPException on duplicate employee_id."""
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

async def list_employees(
    filter_query: Dict[str, Any],
    page: int,
    size: int,
    sort_by: str,
    order: str
) -> List[Dict[str, Any]]:
    skip = (page - 1) * size
    sort_dir = ASCENDING if order == "asc" else DESCENDING
    cursor = employees_collection.find(filter_query).sort(sort_by, sort_dir).skip(skip).limit(size)
    docs = await cursor.to_list(length=size)
    return [_doc_to_employee(d) for d in docs]

async def count_employees(filter_query: Dict[str, Any]) -> int:
    return await employees_collection.count_documents(filter_query)
