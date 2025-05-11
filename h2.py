from fastapi import FastAPI, Request, HTTPException
import httpx
import os

app = FastAPI()

# Replace these with your actual details or load them securely
SERVICE_BUS_NAMESPACE = "your-namespace.servicebus.windows.net"
QUEUE_NAME = "your-queue-name"
SHARED_ACCESS_SIGNATURE = "SharedAccessSignature sr=..."  # full token here

@app.post("/genesys-webhook")
async def genesys_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Send message to Azure Service Bus
    service_bus_url = f"https://{SERVICE_BUS_NAMESPACE}/{QUEUE_NAME}/messages"

    headers = {
        "Authorization": SHARED_ACCESS_SIGNATURE,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(service_bus_url, json=data, headers=headers)

    if response.status_code != 201:
        raise HTTPException(status_code=500, detail=f"Failed to send to Azure SB: {response.text}")

    return {"status": "success", "azure_response": response.status_code}








# pip install fastapi uvicorn httpx
# uvicorn your_filename:app --reload

{
  "conversationId": "abc123",
  "event": "callEnded",
  "timestamp": "2025-05-09T10:15:00Z",
  "customer": {
    "id": "cust456",
    "name": "Jane Doe"
  },
  "metadata": {
    "agentId": "agent789",
    "duration": 180
  }
}



####################################################################################################################################
####################################################################################################################################
# pip install azure-servicebus



3. Azure SDK (High-level, Official)
If you want better error handling, message metadata support, retries, and long-term maintainability, use the Azure SDK:

from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage

conn_str = "Endpoint=sb://...;SharedAccessKeyName=...;SharedAccessKey=..."
queue_name = "your-queue"

async def send_to_service_bus(data):
    async with ServiceBusClient.from_connection_string(conn_str) as client:
        sender = client.get_queue_sender(queue_name=queue_name)
        async with sender:
            message = ServiceBusMessage(json.dumps(data))
            await sender.send_messages(message)



####################################################################################################################################
####################################################################################################################################



####################################################################################################################################
####################################################################################################################################


from fastapi import FastAPI, Request, HTTPException
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
import os
import json

app = FastAPI()

# Replace with your Azure Service Bus connection string and queue name
SERVICE_BUS_CONNECTION_STR = "Endpoint=sb://your-namespace.servicebus.windows.net/;SharedAccessKeyName=...;SharedAccessKey=..."
QUEUE_NAME = "your-queue-name"

@app.post("/genesys-webhook")
async def genesys_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    try:
        # Create a Service Bus client
        async with ServiceBusClient.from_connection_string(SERVICE_BUS_CONNECTION_STR) as client:
            sender = client.get_queue_sender(queue_name=QUEUE_NAME)
            async with sender:
                message = ServiceBusMessage(json.dumps(data))
                await sender.send_messages(message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending to Service Bus: {str(e)}")

    return {"status": "success", "message": "Sent to Azure Service Bus"}





####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
# Now let’s filter the payload to ensure we only process messages with outbound direction.
# Here’s how your FastAPI webhook code might look like:

from fastapi import FastAPI, HTTPException, Request
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
import json
import configparser

app = FastAPI()

# Load configuration values from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

SERVICE_BUS_CONNECTION_STR = config['AzureServiceBus']['ConnectionString']
QUEUE_NAME = config['AzureServiceBus']['QueueName']

@app.post("/genesys-webhook")
async def genesys_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Check if direction in the payload is "outbound"
    if data.get("direction") != "outbound":
        return {"status": "skipped", "reason": "Only processing outbound interactions"}

    # Check participants array for "outbound" direction (Agent)
    participants = data.get("participants", [])
    if not any(p.get("direction") == "outbound" for p in participants):
        return {"status": "skipped", "reason": "No outbound direction in participants"}

    try:
        # Create a Service Bus client and send the message
        async with ServiceBusClient.from_connection_string(SERVICE_BUS_CONNECTION_STR) as client:
            sender = client.get_queue_sender(queue_name=QUEUE_NAME)
            async with sender:
                message = ServiceBusMessage(json.dumps(data))  # Wrap payload as message
                await sender.send_messages(message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending to Service Bus: {str(e)}")

    return {"status": "success", "message": "Sent to Azure Service Bus"}


from pydantic import BaseModel
from typing import List, Optional

class Participant(BaseModel):
    participantId: str
    purpose: str
    direction: str

class GenesysPayload(BaseModel):
    conversationId: str
    event: str
    timestamp: str
    direction: str
    participants: List[Participant]
    metadata: Optional[dict] = None


####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################

 # Full FastAPI Webhook Code with Validation
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
import configparser
import json
import logging

app = FastAPI()

# ------------------- Configuration -------------------
config = configparser.ConfigParser()
config.read("config.ini")

try:
    SERVICE_BUS_CONNECTION_STR = config["AzureServiceBus"]["ConnectionString"]
    QUEUE_NAME = config["AzureServiceBus"]["QueueName"]
except KeyError as e:
    raise RuntimeError(f"Missing configuration key: {e}")

# ------------------- Logging Setup -------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("genesys-webhook")

# ------------------- Pydantic Models -------------------
class Participant(BaseModel):
    participantId: str = Field(..., description="Unique ID of the participant")
    purpose: str = Field(..., description="Purpose like 'agent' or 'customer'")
    direction: str = Field(..., description="Direction must be 'inbound' or 'outbound'")

class GenesysPayload(BaseModel):
    conversationId: str
    event: str
    timestamp: str
    direction: str = Field(..., regex="^(inbound|outbound)$", description="Overall direction")
    participants: List[Participant]
    metadata: Optional[dict] = None

# ------------------- Webhook Endpoint -------------------
@app.post("/genesys-webhook")
async def genesys_webhook(request: Request):
    try:
        payload_raw = await request.json()
        payload = GenesysPayload(**payload_raw)
    except ValidationError as ve:
        logger.warning(f"Payload validation failed: {ve}")
        raise HTTPException(status_code=422, detail=ve.errors())
    except Exception as e:
        logger.error(f"Unexpected error parsing JSON: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    # Filter: root-level direction
    if payload.direction.lower() != "outbound":
        return {"status": "skipped", "reason": "Conversation is not outbound"}

    # Filter: at least one outbound participant (usually the agent)
    has_outbound_participant = any(
        p.direction.lower() == "outbound" for p in payload.participants
    )
    if not has_outbound_participant:
        return {"status": "skipped", "reason": "No outbound participant in conversation"}

    # Convert payload to JSON
    try:
        message_body = json.dumps(payload.dict())
    except Exception as e:
        logger.error(f"Error serializing message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to serialize message")

    # Send to Azure Service Bus
    try:
        async with ServiceBusClient.from_connection_string(SERVICE_BUS_CONNECTION_STR) as client:
            sender = client.get_queue_sender(queue_name=QUEUE_NAME)
            async with sender:
                message = ServiceBusMessage(message_body)
                await sender.send_messages(message)
    except Exception as e:
        logger.exception("Failed to send message to Azure Service Bus")
        raise HTTPException(status_code=500, detail=f"Service Bus error: {str(e)}")

    logger.info("Message successfully sent to Azure Service Bus")
    return {"status": "success", "message": "Payload forwarded to Azure Service Bus"}











####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################    








from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
import configparser
import json
import logging
import asyncio

app = FastAPI()

# ------------------ Configuration ------------------
config = configparser.ConfigParser()
config.read("config.ini")

try:
    SERVICE_BUS_CONNECTION_STR = config["AzureServiceBus"]["ConnectionString"]
    QUEUE_NAME = config["AzureServiceBus"]["QueueName"]
except KeyError as e:
    raise RuntimeError(f"Missing configuration key: {e}")

# ------------------ Logging ------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("genesys-webhook")

# ------------------ Pydantic Models ------------------
class Participant(BaseModel):
    participantId: str
    purpose: str
    direction: str

class GenesysPayload(BaseModel):
    conversationId: str
    event: str
    timestamp: str
    direction: str = Field(..., regex="^(inbound|outbound)$")
    participants: List[Participant]
    metadata: Optional[dict] = None

# ------------------ Webhook Endpoint ------------------
@app.post("/genesys-webhook")
async def genesys_webhook(request: Request):
    try:
        payload_raw = await request.json()
        payload = GenesysPayload(**payload_raw)
    except ValidationError as ve:
        logger.warning(f"Validation failed: {ve}")
        raise HTTPException(status_code=422, detail=ve.errors())
    except Exception as e:
        logger.error(f"JSON parsing error: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if payload.direction.lower() != "outbound":
        return {"status": "skipped", "reason": "Conversation is not outbound"}

    has_outbound_participant = any(
        p.direction.lower() == "outbound" for p in payload.participants
    )
    if not has_outbound_participant:
        return {"status": "skipped", "reason": "No outbound participant"}

    try:
        message_body = json.dumps(payload.dict())
    except Exception as e:
        logger.error(f"Serialization error: {e}")
        raise HTTPException(status_code=500, detail="Failed to serialize message")

    try:
        async with ServiceBusClient.from_connection_string(SERVICE_BUS_CONNECTION_STR) as client:
            sender = client.get_queue_sender(queue_name=QUEUE_NAME)
            async with sender:
                for attempt in range(3):  # Retry logic
                    try:
                        message = ServiceBusMessage(message_body)
                        await sender.send_messages(message)
                        logger.info("Message sent to Azure Service Bus")
                        return {"status": "success", "message": "Payload forwarded"}
                    except Exception as e:
                        logger.warning(f"Attempt {attempt+1} failed: {e}")
                        if attempt < 2:
                            await asyncio.sleep(2 ** attempt)  # exponential backoff
                        else:
                            raise HTTPException(status_code=500, detail="Final Service Bus failure")
    except Exception as e:
        logger.exception("Service Bus client error")
        raise HTTPException(status_code=500, detail=f"Service Bus client error: {e}")






#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

import azure.functions as func
from pydantic import BaseModel, ValidationError, Field
from typing import List, Optional
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
import configparser
import json
import asyncio
import logging

# Setup
config = configparser.ConfigParser()
config.read("config.ini")

SERVICE_BUS_CONNECTION_STR = config["AzureServiceBus"]["ConnectionString"]
QUEUE_NAME = config["AzureServiceBus"]["QueueName"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webhook")

# Pydantic Models
class Participant(BaseModel):
    participantId: str
    purpose: str
    direction: str

class GenesysPayload(BaseModel):
    conversationId: str
    event: str
    timestamp: str
    direction: str = Field(..., regex="^(inbound|outbound)$")
    participants: List[Participant]
    metadata: Optional[dict] = None

# Azure Function entrypoint
async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        payload_raw = req.get_json()
        payload = GenesysPayload(**payload_raw)
    except ValidationError as ve:
        return func.HttpResponse(str(ve), status_code=422)
    except Exception as e:
        return func.HttpResponse("Invalid JSON", status_code=400)

    if payload.direction.lower() != "outbound":
        return func.HttpResponse("Skipped: not outbound", status_code=200)

    has_outbound = any(p.direction.lower() == "outbound" for p in payload.participants)
    if not has_outbound:
        return func.HttpResponse("Skipped: no outbound participant", status_code=200)

    message_body = json.dumps(payload.dict())
    try:
        async with ServiceBusClient.from_connection_string(SERVICE_BUS_CONNECTION_STR) as client:
            sender = client.get_queue_sender(queue_name=QUEUE_NAME)
            async with sender:
                for attempt in range(3):
                    try:
                        await sender.send_messages(ServiceBusMessage(message_body))
                        return func.HttpResponse("Success", status_code=200)
                    except Exception as e:
                        if attempt < 2:
                            await asyncio.sleep(2 ** attempt)
                        else:
                            return func.HttpResponse("Service Bus failure", status_code=500)
    except Exception as e:
        logger.error(f"Unhandled SB client error: {e}")
        return func.HttpResponse("SB client error", status_code=500)



{
  "bindings": [
    {
      "authLevel": "anonymous",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["post"]
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    }
  ]
}


#ini  
[AzureServiceBus]
ConnectionString = <your_connection_string>
QueueName = <your_queue>

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# pip install fastapi uvicorn azure-servicebus



from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from azure.servicebus import ServiceBusClient, ServiceBusMessage
import os

app = FastAPI()

# Replace with your actual Azure Service Bus details
SERVICE_BUS_NAMESPACE = "your-namespace.servicebus.windows.net"
QUEUE_NAME = "your-queue-name"
SHARED_ACCESS_SIGNATURE = "your-SAS-token"

# Pydantic model to validate input (adjust fields to your expected Genesys data)
class GenesysPayload(BaseModel):
    # Example fields
    user_id: str
    message: str
    timestamp: str

def send_to_service_bus(payload: dict):
    try:
        servicebus_client = ServiceBusClient(
            fully_qualified_namespace=SERVICE_BUS_NAMESPACE,
            credential=SHARED_ACCESS_SIGNATURE
        )

        with servicebus_client:
            sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
            with sender:
                message = ServiceBusMessage(str(payload))
                sender.send_messages(message)

    except Exception as e:
        raise RuntimeError(f"Error sending message to Service Bus: {e}")

@app.post("/webhook")
async def webhook_handler(payload: GenesysPayload):
    try:
        data_dict = payload.dict()
        send_to_service_bus(data_dict)
        return {"status": "Message sent to Azure Service Bus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# uvicorn webhook:app --reload --host 0.0.0.0 --port 8000

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@



[azure_service_bus]
SERVICE_BUS_NAMESPACE = your-namespace.servicebus.windows.net
QUEUE_NAME = your-queue-name



import asyncio
import random
import configparser

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
from azure.identity.aio import DefaultAzureCredential

app = FastAPI()

# Load config from ini
config = configparser.ConfigParser()
config.read('config.ini')

SERVICE_BUS_NAMESPACE = config.get('azure_service_bus', 'SERVICE_BUS_NAMESPACE')
QUEUE_NAME = config.get('azure_service_bus', 'QUEUE_NAME')

# Pydantic model for incoming request
class GenesysPayload(BaseModel):
    user_id: str
    message: str
    timestamp: str

# Async message sender with exponential backoff and jitter
async def send_to_service_bus_async(payload: dict, max_retries: int = 5, base_delay: float = 1.0):
    credential = DefaultAzureCredential()
    
    async with ServiceBusClient(
        fully_qualified_namespace=SERVICE_BUS_NAMESPACE,
        credential=credential
    ) as servicebus_client:
        
        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        
        async with sender:
            for attempt in range(max_retries):
                try:
                    message = ServiceBusMessage(str(payload))
                    await sender.send_messages(message)
                    return  # Success
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise RuntimeError(f"Failed after {max_retries} attempts: {e}")
                    delay = random.uniform(0, base_delay * (2 ** attempt))  # Jitter
                    await asyncio.sleep(delay)

# FastAPI webhook endpoint
@app.post("/webhook")
async def webhook_handler(payload: GenesysPayload):
    try:
        await send_to_service_bus_async(payload.dict())
        return {"status": "Message sent to Azure Service Bus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




################################################################################################################

[azure_service_bus]
SERVICE_BUS_NAMESPACE = your-namespace.servicebus.windows.net
QUEUE_NAME = your-queue-name


import asyncio
import random
import configparser

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
from azure.identity.aio import DefaultAzureCredential

# ----------------------------
# Load config from ini
# ----------------------------
config = configparser.ConfigParser()
config.read('config.ini')

SERVICE_BUS_NAMESPACE = config.get('azure_service_bus', 'SERVICE_BUS_NAMESPACE')
QUEUE_NAME = config.get('azure_service_bus', 'QUEUE_NAME')

# ----------------------------
# FastAPI instance
# ----------------------------
app = FastAPI()

# ----------------------------
# Genesys Payload Model
# ----------------------------
class GenesysPayload(BaseModel):
    user_id: str
    message: str
    timestamp: str  # Use datetime if you want automatic parsing

# ----------------------------
# Async message sender with retry
# ----------------------------
async def send_to_service_bus_async(payload: dict, max_retries: int = 5, base_delay: float = 1.0):
    credential = DefaultAzureCredential()

    async with ServiceBusClient(
        fully_qualified_namespace=SERVICE_BUS_NAMESPACE,
        credential=credential
    ) as servicebus_client:

        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)

        async with sender:
            for attempt in range(max_retries):
                try:
                    message = ServiceBusMessage(str(payload))
                    await sender.send_messages(message)
                    return
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise RuntimeError(f"Failed after {max_retries} attempts: {e}")
                    delay = random.uniform(0, base_delay * (2 ** attempt))
                    await asyncio.sleep(delay)

# ----------------------------
# Webhook endpoint
# ----------------------------
@app.post("/webhook")
async def webhook_handler(payload: GenesysPayload):
    try:
        data = payload.dict()

        # Send message to Azure Service Bus
        await send_to_service_bus_async(data)

        return {"status": "Message sent to Azure Service Bus"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
