from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import os
import asyncio
import json
from typing import AsyncGenerator

import logfire
from pymongo.errors import PyMongoError
from fastapi.middleware.cors import CORSMiddleware
import nest_asyncio
from dotenv import load_dotenv

# To this (fix the import paths)
from app.controller import data_model_controller
from app.controller import collection_controller

# Load environment variables
load_dotenv('.env')

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    yield
    # Shutdown logic goes here if needed

app = FastAPI(lifespan=lifespan)
nest_asyncio.apply()

# Configure CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logfire
log = logfire.configure()
logfire.instrument_fastapi(app)
logfire.instrument_pymongo(capture_statement=True)

# Include routers
app.include_router(data_model_controller.router, prefix="/model", tags=["Data Model"])
app.include_router(collection_controller.router, prefix="/collection", tags=["Collection"])

# Define OpenAPI export function
def export_openapi():
    """Export OpenAPI specification to a file"""
    with open("openapi.json", "w") as f:
        json.dump(app.openapi(), f, indent=2)




if __name__ == '__main__':
    export_openapi()
    import uvicorn
    port = int(os.environ.get('PORT', 63342))
    uvicorn.run("app.application:app", host="0.0.0.0", port=port, reload=True)