import asyncio
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusSubQueue

# Update with your Azure Service Bus connection string and queue name
CONNECTION_STR = "Endpoint=sb://<your-namespace>.servicebus.windows.net/;SharedAccessKeyName=<keyname>;SharedAccessKey=<key>"
QUEUE_NAME = "<your-queue-name>"


async def read_dead_letter_messages(connection_str: str, queue_name: str):
    """
    Reads messages from the dead letter queue and prints their dead letter reason and description.
    """
    print(f"Connecting to DLQ of queue: {queue_name}")

    # Create a ServiceBusClient
    servicebus_client = ServiceBusClient.from_connection_string(
        conn_str=connection_str,
        logging_enable=True
    )

    async with servicebus_client:
        # Get the DLQ receiver
        receiver = servicebus_client.get_queue_receiver(
            queue_name=queue_name,
            sub_queue=ServiceBusSubQueue.DEAD_LETTER
        )

        async with receiver:
            print("Receiving messages from Dead Letter Queue...\n")
            messages = await receiver.receive_messages(
                max_message_count=10,
                max_wait_time=5
            )

            if not messages:
                print("✅ No messages in the Dead Letter Queue.")
                return

            for i, message in enumerate(messages, start=1):
                print(f"----- DLQ Message {i} -----")
                print(f"Message ID               : {message.message_id}")
                print(f"Body                     : {str(message)}")
                print(f"Dead Letter Reason       : {message.dead_letter_reason}")
                print(f"Dead Letter Description  : {message.dead_letter_error_description}")
                print(f"Enqueued Time (UTC)      : {message.enqueued_time_utc}")
                print("---------------------------\n")

                # Optional: complete (remove from DLQ) or defer
                await receiver.complete_message(message)


if __name__ == "__main__":
    asyncio.run(read_dead_letter_messages(CONNECTION_STR, QUEUE_NAME))
