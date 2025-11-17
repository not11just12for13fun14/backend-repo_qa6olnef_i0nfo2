from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os
from database import db

app = FastAPI(title="Triosept Design Studio API")

# CORS
frontend_url = os.getenv("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    message: str


@app.get("/")
def root():
    return {"message": "Backend is running", "service": "triosept-api"}


@app.get("/test")
def test_db():
    # basic DB visibility (doesn't write)
    if db is None:
        return {
            "backend": "ok",
            "database": "not configured",
            "connection_status": "Database not available. Set DATABASE_URL and DATABASE_NAME",
        }
    try:
        collections = db.list_collection_names()
        return {
            "backend": "ok",
            "database": "configured",
            "database_url": os.getenv("DATABASE_URL", "hidden"),
            "database_name": os.getenv("DATABASE_NAME", "unset"),
            "connection_status": "ok",
            "collections": collections,
        }
    except Exception as e:
        return {
            "backend": "ok",
            "database": "configured",
            "connection_status": f"error: {str(e)}",
        }


@app.post("/contact")
def submit_contact(payload: ContactMessage):
    # If Mongo is configured, store; else just echo back
    if db is not None:
        doc = payload.model_dump()
        doc["source"] = "website"
        db["contact"].insert_one(doc)
    return {"status": "received", "name": payload.name}
