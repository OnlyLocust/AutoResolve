from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC_NAME = "build-logs"

async def create_kafka_topic():
    admin_client = AIOKafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await admin_client.start()
    try:
        topics = await admin_client.list_topics()
        if TOPIC_NAME not in topics:
            new_topic = NewTopic(
                name=TOPIC_NAME,
                num_partitions=4,
                replication_factor=1
            )
            await admin_client.create_topics([new_topic])
            print(f"✅ Created Kafka topic: {TOPIC_NAME}")
    except Exception as e:
        print(f"⚠️ Kafka Topic setup error (may already exist): {e}")
    finally:
        await admin_client.close()

def get_kafka_producer() -> AIOKafkaProducer:
    return AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

def get_kafka_consumer(group_id: str = "log-processors") -> AIOKafkaConsumer:
    return AIOKafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=group_id,
        auto_offset_reset="earliest"
    )