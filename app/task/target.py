# app/tasks/data_extension.py
from celery import Celery
import os
import json
from app.model.data_model import DataModel, get_data_model_primary_keys
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
def generate_target(self, query, collection_id, data_model_dict):
    """ Generate a single target for a collection """
    # read the existing documents in the collection

    # read all the documents in the collection
    collection = mongo_service.get_collection(collection_id)
    documents = collection.find()
    # marshal documents to DataModel
    documents = [DataModel(**doc) for doc in documents]
    # get the primary keys
    doc_keys = get_data_model_primary_keys(documents)

    # Create data model instance from dict
    data_model = DataModel(**data_model_dict)

    # Call the assistant to extend the database
    # Pass the database as context for the assistant
    query = f"""
    Find additional search targets which ARE NOT already in the collection: {json.dumps(doc_keys)}"
    """
    response = assistant(_query=query, _data_model=data_model)

    # Extract result data
    new_target = response.data
    # primary field
    new_target_primary_field = new_target[data_model_dict["primary_field"]]
    # check if the new target is already in the collection
    if new_target_primary_field in doc_keys:
        log.info(f"Target already exists: {new_target_primary_field}")
        return None

    # add the new target to the collection
    mongo_service.insert_document(collection_id, new_target)
    log.info(f"New target added: {new_target_primary_field}")
    return new_target

