# app/services/data_extension_service.py
from typing import List, Dict, Any, AsyncGenerator
from app.model.data_model import DataModel

from app.database.db import MongoDBService


class CollectionService:
    def __init__(self, mongo_service: MongoDBService):
        self.mongo_service = mongo_service

    def create_collection(self, data_model: DataModel, initial_data: List[Dict[str, Any]]) -> str | None:
        """Create a batch of documents """
        # Create a collection for this batch
        collection_name = self.mongo_service.create_collection("collection_")

        # Create a metadata database
        metadata = {
            "_id": "metadata",
            "data_model": data_model.dict(),
            "total_documents": len(initial_data),
            "completed_documents": 0,
            "failed_documents": 0,
            "status": "processing"
        }
        self.mongo_service.insert_documents(collection_name, [metadata])

        # Prepare documents with status fields
        for doc in initial_data:
            doc["_status"] = "pending"
            doc["_retries"] = 0

        # Insert all documents if any
        if initial_data:
            doc_ids = self.mongo_service.insert_documents(collection_name, initial_data)

        return collection_name

    async def stream_collection_updates(self, collection_name: str, request) -> AsyncGenerator[str, None]:
        """Stream updates from a collection"""
        async for update in self.mongo_service.watch_collection(collection_name, request):
            yield update

    def update_data_model(self, collection_name: str, new_data_model: DataModel) -> Dict[str, Any]:
        """Update data model and database schema"""
        # Get existing data model
        metadata = self.mongo_service.get_document(collection_name, "metadata")
        if not metadata or "data_model" not in metadata:
            log.error(f"Metadata or data model not found for collection {collection_name}")
            return {"success": False, "error": "Metadata not found"}

        old_data_model = DataModel(**metadata["data_model"])

        # Find new fields
        old_field_names = set(field.name for field in old_data_model.fields)
        new_field_names = set(field.name for field in new_data_model.fields)

        # Fields to add
        added_fields = new_field_names - old_field_names

        # Update database schema to include new fields
        schema_update_result = self.mongo_service.update_schema(collection_name, list(added_fields))

        # Update metadata with new data model
        metadata_update_success = self.mongo_service.update_metadata_schema(
            collection_name,
            new_data_model.dict()
        )

        return {
            "success": True,
            "added_fields": list(added_fields),
            "documents_updated": schema_update_result["modified_count"],
            "metadata_updated": metadata_update_success
        }
