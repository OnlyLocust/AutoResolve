from kafka_setup import get_kafka_producer, TOPIC_NAME
from schemas.kafka_message import KafkaMessage

producer = get_kafka_producer()

async def start_producer():
    await producer.start()

async def stop_producer():
    await producer.stop()

async def send_log_chunk(message: KafkaMessage):
    key_bytes = message.repo_name.encode('utf-8')
    value_bytes = message.model_dump_json().encode('utf-8')

    # Key guarantees chunks from the same repo land on the same partition
    await producer.send_and_wait(
        TOPIC_NAME,
        key=key_bytes,
        value=value_bytes
    )