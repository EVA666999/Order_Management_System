from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from app.core.config import settings

async def get_kafka_producer():
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
    )
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()