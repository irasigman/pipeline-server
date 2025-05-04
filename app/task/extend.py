# app/tasks/data_extension.py
from celery import Celery
import os
import json
from app.model.data_model import DataModel
from app.database.db import MongoDBService
from demos.extender import assistant
import logfire

# Configure Celery
app = Celery('lux',
             broker='redis://raspberrypi.local:6379/0',
             backend='redis://raspberrypi.local:6379/0')

# MongoDB connection from the service


mongo_service = MongoDBService(
    connection_string=os.environ.get("MONGODB_URI",
                                     "mongodb+srv://irasigman:bushdid311@cluster0.ynkgimh.mongodb.net/?appName=Cluster0"),
    database_name="lux"
)


@app.task(bind=True, max_retries=2, acks_late=True)
def extend_document(self, collection_name, document_id, data_model_dict):
    """Process a single database with AI extension"""
    try:
        # Get database to extend
        document = mongo_service.get_document(collection_name, document_id)
        if not document:
            log.error(f"Document not found: {document_id}")
            return None

        # Mark as processing
        mongo_service.update_document(
            collection_name,
            document_id,
            {"_status": "processing"}
        )

        # Create data model instance from dict
        data_model = DataModel(**data_model_dict)

        # Call the assistant to extend the database
        # Pass the database as context for the assistant
        query = f"Extend this database with all missing information: {json.dumps(document)}"
        response = assistant(_query=query, _data_model=data_model)

        # Extract result data
        extended_data = response.data

        # Update database with extension results
        updates = {}
        if isinstance(extended_data, list):
            # Handle list result
            updates = extended_data[0] if extended_data else {}
        elif isinstance(extended_data, dict):
            # Handle dict result
            updates = extended_data

        # Add status field and remove any private fields
        updates.update({"_status": "completed"})

        # Update the database
        mongo_service.update_document(collection_name, document_id, updates)

        # Update metadata
        mongo_service.update_document(
            collection_name,
            "metadata",
            {"$inc": {"completed_documents": 1}}
        )

        log.info(f"Successfully extended database {document_id}")
        return {"status": "success", "document_id": document_id}

    except Exception as e:
        log.error(f"Error processing database {document_id}: {str(e)}")

        # Get retry count from database
        document = mongo_service.get_document(collection_name, document_id)
        retries = document.get("_retries", 0) + 1

        # Update error information
        mongo_service.update_document(
            collection_name,
            document_id,
            {
                "_error": str(e),
                "_retries": retries,
                "_status": "error"
            }
        )

        # Determine if we should retry
        if retries <= 2:
            # Retry with exponential backoff
            backoff = 60 * (2 ** (retries - 1))  # 60s, 120s
            raise self.retry(exc=e, countdown=backoff)
        else:
            # Mark as permanently failed
            mongo_service.update_document(
                collection_name,
                document_id,
                {"_status": "failed"}
            )

            # Update metadata
            mongo_service.update_document(
                collection_name,
                "metadata",
                {"$inc": {"failed_documents": 1}}
            )

            return {"status": "failed", "document_id": document_id, "error": str(e)}