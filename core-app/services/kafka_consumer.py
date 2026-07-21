import json
import asyncio
from kafka_setup import get_kafka_consumer
from schemas.kafka_message import KafkaMessage
from services.build_state import track_chunk_received

consumer = get_kafka_consumer()
consumer_task = None

async def start_consumer():
    await consumer.start()
    print("🎧 Kafka Consumer started. Listening for chunks...")
    global consumer_task
    consumer_task = asyncio.create_task(consume_messages())

async def stop_consumer():
    if consumer_task:
        consumer_task.cancel()
    await consumer.stop()

async def consume_messages():
    try:
        async for msg in consumer:
            data = json.loads(msg.value.decode('utf-8'))
            message = KafkaMessage(**data)

            # Reassemble tracking via Redis
            all_received = await track_chunk_received(
                message.build_id,
                message.total_chunks
            )

            if all_received:
                print(f"🚀 Build {message.build_id}: All {message.total_chunks} chunks received! Triggering AI Classification...")
                # Classification service call goes here tomorrow
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"❌ Error consuming messages: {e}")