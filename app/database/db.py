# app/services/mongodb_service.py
import uuid
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from pymongo import MongoClient, ReturnDocument
from pymongo.collection import Collection
import json


class MongoDBService:
    def __init__(self, connection_string: str, database_name: str):
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]

    def create_collection(self, name_prefix: str) -> str:
        """Create a new collection with a unique identifier"""
        collection_id = uuid.uuid4().hex
        collection_name = f"{name_prefix}_{collection_id}"
        return collection_name

    def get_collection(self, collection_name: str) -> Collection:
        """Get a MongoDB collection by name"""
        return self.db[collection_name]

    def insert_documents(self, collection_name: str, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert documents into a collection with unique IDs"""
        collection = self.get_collection(collection_name)

        # Ensure each database has an _id
        for doc in documents:
            if '_id' not in doc:
                doc['_id'] = uuid.uuid4().hex

        result = collection.insert_many(documents)
        return result.inserted_ids

    def update_document(self, collection_name: str, doc_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a database in the collection"""
        collection = self.get_collection(collection_name)

        result = collection.find_one_and_update(
            {"_id": doc_id},
            {"$set": updates},
            return_document=ReturnDocument.AFTER
        )
        return result

    def get_document(self, collection_name: str, doc_id: str) -> Dict[str, Any]:
        """Get a database by ID"""
        collection = self.get_collection(collection_name)
        return collection.find_one({"_id": doc_id})

    async def watch_collection(self, collection_name: str, request=None) -> AsyncGenerator[str, None]:
        """Stream changes from a collection"""
        collection = self.get_collection(collection_name)
        change_stream = collection.watch(full_document="updateLookup")

        try:
            while change_stream.alive:
                # Check if client disconnected
                if request and await request.is_disconnected():
                    break

                try:
                    change = await asyncio.to_thread(change_stream.next)
                    yield json.dumps(change, default=str) + "\n"
                except StopIteration:
                    break
        finally:
            change_stream.close()

    def update_schema(self, collection_name: str, new_fields: List[str]):
        """Update all documents in a collection to include new fields"""
        collection = self.get_collection(collection_name)

        # Prepare update with empty values for new fields
        update_fields = {field: "" for field in new_fields}

        # Update all documents except metadata
        result = collection.update_many(
            {"_id": {"$ne": "metadata"}},  # Exclude metadata database
            {"$set": update_fields},
            upsert=False
        )

        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count
        }

    def update_metadata_schema(self, collection_name: str, data_model: Dict[str, Any]):
        """Update the metadata database with new data model"""
        collection = self.get_collection(collection_name)

        result = collection.update_one(
            {"_id": "metadata"},
            {"$set": {"data_model": data_model}}
        )

        return result.modified_count > 0

    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> str:
        """Insert a single database into a collection with a unique ID"""
        collection = self.get_collection(collection_name)

        # Ensure database has an _id
        if '_id' not in document:
            document['_id'] = uuid.uuid4().hex

        # Insert the database
        result = collection.insert_one(document)

        return result.inserted_id
