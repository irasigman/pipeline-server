import asyncio
import json
from typing import AsyncGenerator

from fastapi import FastAPI, Request
import logfire
from pymongo.errors import PyMongoError

from app.controller import data_model_controller
from demos.dice_roll import assistant
import nest_asyncio

from dotenv import load_dotenv

load_dotenv('./.env')

app = FastAPI()
nest_asyncio.apply()

# log = logfire.configure()
# logfire.instrument_fastapi(app)
# logfire.instrument_pymongo(capture_statement=True)

from demos.mongodb import write_demo, client, collection

app.include_router(data_model_controller.router, prefix="/model", tags=["Data Model"])

@app.post("/")
async def get_response(request: Request):
    """
    This function is used to get a response from the assistant.
    :param request:
    :return:
    """
    body = await request.json()
    query = body.get("query")
    response = await assistant(query)
    return response

@app.get("/")
def write_response():
    """
    This function is used to get a response from the assistant.
    :return:
    """
    done = write_demo()
    return {"done": True}



from fastapi.responses import StreamingResponse



async def generate_changes(request: Request) -> AsyncGenerator[str, None]:
    """
    Generate a stream of all changes from MongoDB collection
    """
    change_stream = collection.watch(full_document="updateLookup")

    try:
        while change_stream.alive:
            # Check if the client has disconnected
            if await request.is_disconnected():
                break
            try:
                change = await asyncio.to_thread(change_stream.next)
                yield json.dumps(change, default=str) + "\n"
            except StopIteration:
                break
    finally:
        change_stream.close()


@app.get("/subscribe")
async def subscribe_to_changes(request: Request):
    """
    Subscribe to all changes from the MongoDB collection in real-time
    """
    return StreamingResponse(
        generate_changes(request),
        media_type="application/x-ndjson"
    )