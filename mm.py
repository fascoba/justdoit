from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils import (
    init_clients,
    close_clients,
    send_message_to_queue,
    upsert_item_to_cosmos
)

app = FastAPI(title="Azure FastAPI App")

# Pydantic models for request body
class MessageRequest(BaseModel):
    message: str
    item_id: str
    data: dict

@app.on_event("startup")
async def startup_event():
    """Initialize shared Azure clients on app startup."""
    await init_clients()

@app.on_event("shutdown")
async def shutdown_event():
    """Close Azure clients on app shutdown."""
    await close_clients()

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
        # Send message to Service Bus
        await send_message_to_queue(request.message)

        # Upsert item in Cosmos DB
        await upsert_item_to_cosmos(request.item_id, request.data)

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
