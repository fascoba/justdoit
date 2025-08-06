import os
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

# Environment variables
SERVICE_BUS_CONNECTION_STR = os.getenv("SERVICE_BUS_CONNECTION_STR")
SERVICE_BUS_QUEUE_NAME = os.getenv("SERVICE_BUS_QUEUE_NAME")
COSMOS_DB_URI = os.getenv("COSMOS_DB_URI")
COSMOS_DB_KEY = os.getenv("COSMOS_DB_KEY")
COSMOS_DB_NAME = os.getenv("COSMOS_DB_NAME")
COSMOS_DB_CONTAINER = os.getenv("COSMOS_DB_CONTAINER")

# Global clients
service_bus_client = None
cosmos_client = None
cosmos_container = None

async def init_clients():
    """Initialize all Azure clients (Service Bus and Cosmos DB)."""
    await init_service_bus_client()
    await init_cosmos_client()

async def close_clients():
    """Close all Azure clients."""
    await close_service_bus_client()
    await close_cosmos_client()

# -----------------------------
# Service Bus related functions
# -----------------------------
async def init_service_bus_client():
    """Initialize Service Bus client."""
    global service_bus_client
    if not SERVICE_BUS_CONNECTION_STR:
        raise ValueError("SERVICE_BUS_CONNECTION_STR is missing.")
    service_bus_client = ServiceBusClient.from_connection_string(SERVICE_BUS_CONNECTION_STR)

async def close_service_bus_client():
    """Close Service Bus client."""
    global service_bus_client
    if service_bus_client:
        await service_bus_client.close()

async def send_message_to_queue(message: str):
    """Send a message to the Azure Service Bus queue."""
    if not service_bus_client:
        raise RuntimeError("Service Bus client is not initialized.")
    if not SERVICE_BUS_QUEUE_NAME:
        raise ValueError("SERVICE_BUS_QUEUE_NAME is missing.")
    
    sender = service_bus_client.get_queue_sender(queue_name=SERVICE_BUS_QUEUE_NAME)
    async with sender:
        await sender.send_messages(ServiceBusMessage(message))

# -----------------------------
# Cosmos DB related functions
# -----------------------------
async def init_cosmos_client():
    """Initialize Cosmos DB client and container."""
    global cosmos_client, cosmos_container
    if not all([COSMOS_DB_URI, COSMOS_DB_KEY, COSMOS_DB_NAME, COSMOS_DB_CONTAINER]):
        raise ValueError("Cosmos DB configuration is missing.")
    
    cosmos_client = CosmosClient(COSMOS_DB_URI, credential=COSMOS_DB_KEY)
    database = cosmos_client.get_database_client(COSMOS_DB_NAME)
    cosmos_container = database.get_container_client(COSMOS_DB_CONTAINER)

async def close_cosmos_client():
    """Close Cosmos DB client."""
    global cosmos_client
    if cosmos_client:
        await cosmos_client.close()

async def upsert_item_to_cosmos(item_id: str, data: dict):
    """Upsert an item into Azure Cosmos DB container."""
    if not cosmos_container:
        raise RuntimeError("Cosmos DB client is not initialized.")
    
    try:
        item = {"id": item_id, **data}
        await cosmos_container.upsert_item(item)
    except CosmosHttpResponseError as e:
        raise RuntimeError(f"Failed to upsert item: {e}")
