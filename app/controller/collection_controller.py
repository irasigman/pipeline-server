# app/controllers/data_extension_controller.py
import json
from typing import List, Dict, Any
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.database.db import MongoDBService
from app.task.target import generate_target

from app.model.data_model import DataModel

import os

from app.service.collection import CollectionService

# Create services
mongo_service = MongoDBService(
    connection_string=os.environ.get("MONGODB_URI",
                                     "mongodb+srv://irasigman:bushdid311@cluster0.ynkgimh.mongodb.net/?appName=Cluster0"),
    database_name="lux"
)

collection_service = CollectionService(mongo_service)

router = APIRouter()


class CreateCollectionRequest(BaseModel):
    data_model: DataModel
    initial_data: List[Dict[str, Any]] = Field(..., description="Initial data objects")

class CreateCollectionResponse(BaseModel):
    collection_id: str = Field(..., description="Collection ID for monitoring progress")
    document_count: int = Field(..., description="Number of documents in the batch")

class AddDocumentRequest(BaseModel):
    data_model: DataModel
    collection_id: str = Field(..., description="Collection ID to monitor progress")
    document_count: int = Field(..., description="Number of documents in the batch")

class AddDocumentResponse(BaseModel):
    collection_id: str = Field(..., description="Collection ID for monitoring progress")

@router.post("/", response_model=CreateCollectionResponse)
async def create_collection(request: CreateCollectionRequest):
    """
    Create a batch of data extension jobs

    Takes a data model and initial objects, creates jobs to extend each object
    with AI-generated content, and returns a collection ID for monitoring.
    """
    try:
        collection_id = collection_service.create_collection(
            request.data_model,
            request.initial_data
        )

        return CreateCollectionResponse(
            collection_id=collection_id,
            document_count=len(request.initial_data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add_document", response_model=AddDocumentResponse)
async def add_document(request: AddDocumentRequest):
    """
    Run a single job to identify more targets, and add to collection
    """
    data_model_dict = request.data_model.dict()
    collection_id = request.collection_id

    # Create a queue specific to this collection
    queue_name = f"collection_{collection_id}"

    # Submit tasks to the collection-specific queue
    for i in range(request.document_count):
        query = f"Find target #{i + 1}"
        generate_target.apply_async(
            args=[query, collection_id, data_model_dict],
            queue=queue_name
        )

    return AddDocumentResponse(collection_id=collection_id)

@router.get("/stream/{collection_id}")
async def stream_updates(collection_id: str, request: Request):
    """
    Stream real-time updates from a collection

    Returns a server-sent events stream of database changes
    for monitoring extension progress.
    """

    async def generate_updates():
        async for update in collection_service.stream_collection_updates(collection_id, request):
            yield f"data: {update}\n\n"

    return StreamingResponse(
        generate_updates(),
        media_type="text/event-stream"
    )

# celery -A app.task.target worker -Q "collection_*" --concurrency=1 --hostname=collector@%h