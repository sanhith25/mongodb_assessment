
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "assessment_db")

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]
employees_collection = db["employees"]
