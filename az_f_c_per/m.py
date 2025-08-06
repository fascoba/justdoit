from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from u import (
    init_clients,
    close_clients,
    send_message_to_queue,
    upsert_item_to_cosmos
)

class MessageRequest(BaseModel):
    message: str
    item_id: str
    data: dict

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_clients()
    yield
    # Shutdown
    await close_clients()

app = FastAPI(title="Azure FastAPI App", lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/process")
async def process_message(request: MessageRequest):
    """
    - Sends a message to Azure Service Bus Queue.
    - Upserts an item into Azure Cosmos DB.
    """
    try:
        await send_message_to_queue(request.message)
        await upsert_item_to_cosmos(request.item_id, request.data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
