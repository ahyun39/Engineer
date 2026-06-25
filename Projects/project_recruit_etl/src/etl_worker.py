"""ETL Worker — Kafka Consumer.

saramin-jobs-raw 토픽을 구독해 메시지를 누적하고,
마지막 메시지 수신 후 FLUSH_SECONDS 초가 지나면 배치를 Transform → Save한다.

실행: python etl_worker.py
종료: Ctrl+C (진행 중인 배치가 있으면 처리 후 종료)
"""

import json
from datetime import datetime

import pandas as pd
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from .config import KAFKA_BOOTSTRAP, KAFKA_TOPIC, KAFKA_GROUP_ID, FLUSH_SECONDS, POLL_INTERVAL_MS
from .transformer import transform, log_data_quality, save_processed
from .loader import load
from .log_config import get_logger

logger = get_logger(__name__)


def _deserialize(v):
    """JSON 파싱 실패 시 None 반환 (ping 등 비JSON 메시지 무시)"""
    if not v:
        return None
    try:
        return json.loads(v.decode("utf-8"))
    except Exception:
        return None


def process_batch(records: list):
    logger.info("배치 처리 시작: %d건", len(records))
    df = pd.DataFrame(records)
    df = transform(df)
    log_data_quality(df)
    save_processed(df)
    load(df)
    logger.info("배치 처리 완료")


def run():
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            group_id=KAFKA_GROUP_ID,
            auto_offset_reset="earliest",    # 처음 실행 시 가장 오래된 메시지부터
            enable_auto_commit=False,        # 수동 커밋: process_batch 완료 후에만 커밋
            value_deserializer=_deserialize,
        )
    except NoBrokersAvailable:
        raise RuntimeError(
            f"Kafka 브로커에 연결할 수 없습니다: {KAFKA_BOOTSTRAP}\n"
            "docker compose up -d 로 Kafka를 먼저 실행해주세요."
        )

    logger.info("=== ETL Worker 대기 중 (topic=%s, group=%s) ===", KAFKA_TOPIC, KAFKA_GROUP_ID)

    batch = []
    last_received_at = None

    try:
        while True:
            # poll: POLL_INTERVAL_MS 동안 대기하며 메시지 수신
            poll_result = consumer.poll(timeout_ms=POLL_INTERVAL_MS)

            if poll_result:
                for messages in poll_result.values():
                    for msg in messages:
                        if msg.value is None:   # 비JSON 메시지(ping 등) 무시
                            continue
                        batch.append(msg.value)
                last_received_at = datetime.now()
                logger.debug("메시지 누적: %d건 (offset=%d)", len(batch), msg.offset)

            # 배치가 있고 FLUSH_SECONDS 이상 신규 메시지가 없으면 처리
            if batch and last_received_at:
                idle_seconds = (datetime.now() - last_received_at).seconds
                if idle_seconds >= FLUSH_SECONDS:
                    process_batch(batch)
                    consumer.commit()        # 배치 처리 완료 후 offset 커밋
                    batch = []
                    last_received_at = None

    except KeyboardInterrupt:
        logger.info("ETL Worker 종료 신호 수신")
    finally:
        if batch:
            logger.info("종료 전 잔여 배치 처리: %d건", len(batch))
            process_batch(batch)
            consumer.commit()
        consumer.close()
        logger.info("ETL Worker 종료 완료")


if __name__ == "__main__":
    run()
