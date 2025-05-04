import random
import uuid

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
uri = "mongodb+srv://irasigman:bushdid311@cluster0.ynkgimh.mongodb.net/?appName=Cluster0"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["demo"]
collection = db["demo"]


def write_to_mongo(data):
    """
    Write data to MongoDB.
    :param data: The data to write.
    :return: The result of the insert operation.
    """
    result = collection.insert_one(data)
    return result.inserted_id

def write_demo():
    """
    Write a demo database to MongoDB.
    :return: The ID of the inserted database.
    """

    data = {
        "_id": uuid.uuid4().hex,
        "name": "John Doe",
        "age": 30,
        "city": "New York"
    }

    result = write_to_mongo(data)
    return result

def update_document_by_id(document_id, update_data):
    """
    Update a database in MongoDB by its ID.
    :param document_id: The ID of the database to update.
    :param update_data: The data to update.
    :return: The result of the update operation.
    """
    result = collection.update_one({"_id": document_id}, {"$set": update_data})
    return result.modified_count

if __name__ == '__main__':
    write_demo()
    print("Data written to MongoDB")