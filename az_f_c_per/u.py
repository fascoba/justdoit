import os
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

# Read from environment (Azure Functions configuration)
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

# ------------------------------
# Global client lifecycle
# ------------------------------
async def init_clients():
    await init_service_bus_client()
    await init_cosmos_client()

async def close_clients():
    await close_service_bus_client()
    await close_cosmos_client()

# ------------------------------
# Service Bus
# ------------------------------
async def init_service_bus_client():
    global service_bus_client
    if not SERVICE_BUS_CONNECTION_STR:
        raise ValueError("SERVICE_BUS_CONNECTION_STR is missing.")
    service_bus_client = ServiceBusClient.from_connection_string(SERVICE_BUS_CONNECTION_STR)

async def close_service_bus_client():
    global service_bus_client
    if service_bus_client:
        await service_bus_client.close()

async def send_message_to_queue(message: str):
    if not service_bus_client:
        raise RuntimeError("Service Bus client not initialized.")
    sender = service_bus_client.get_queue_sender(queue_name=SERVICE_BUS_QUEUE_NAME)
    async with sender:
        await sender.send_messages(ServiceBusMessage(message))

# ------------------------------
# Cosmos DB
# ------------------------------
async def init_cosmos_client():
    global cosmos_client, cosmos_container
    if not all([COSMOS_DB_URI, COSMOS_DB_KEY, COSMOS_DB_NAME, COSMOS_DB_CONTAINER]):
        raise ValueError("Cosmos DB configuration is missing.")
    cosmos_client = CosmosClient(COSMOS_DB_URI, credential=COSMOS_DB_KEY)
    db = cosmos_client.get_database_client(COSMOS_DB_NAME)
    cosmos_container = db.get_container_client(COSMOS_DB_CONTAINER)

async def close_cosmos_client():
    global cosmos_client
    if cosmos_client:
        await cosmos_client.close()

async def upsert_item_to_cosmos(item_id: str, data: dict):
    if not cosmos_container:
        raise RuntimeError("Cosmos DB client not initialized.")
    try:
        item = {"id": item_id, **data}
        await cosmos_container.upsert_item(item)
    except CosmosHttpResponseError as e:
        raise RuntimeError(f"Failed to upsert item: {e}")
