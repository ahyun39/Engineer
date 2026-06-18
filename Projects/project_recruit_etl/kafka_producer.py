"""사람인 채용 공고 Kafka Producer.

scraper.py로 수집한 원시 데이터를 Kafka 토픽에 발행한다.
cron에 의해 하루 2회(11:00, 18:00) 실행된다.
"""

import json

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from scraper import scrape, save_raw
from log_config import get_logger

logger = get_logger(__name__)

KAFKA_BOOTSTRAP = "localhost:9092"
TOPIC = "saramin-jobs-raw"


def create_producer():
    try:
        return KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            value_serializer=lambda v: json.dumps(
                v, ensure_ascii=False, default=str
            ).encode("utf-8"),
            acks="all",          # 브로커 확인 후 전송 완료 처리
            retries=3,
        )
    except NoBrokersAvailable:
        raise RuntimeError(
            f"Kafka 브로커에 연결할 수 없습니다: {KAFKA_BOOTSTRAP}\n"
            "docker compose up -d 로 Kafka를 먼저 실행해주세요."
        )


def produce():
    logger.info("=== Kafka Producer 시작: topic=%s ===", TOPIC)

    df = scrape()
    save_raw(df)

    producer = create_producer()
    sent = 0

    for record in df.to_dict(orient="records"):
        producer.send(TOPIC, value=record)
        sent += 1

    producer.flush()
    producer.close()

    logger.info("Kafka 발행 완료: %d건 → topic=%s", sent, TOPIC)


if __name__ == "__main__":
    produce()
