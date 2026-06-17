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

from transformer import transform, log_data_quality, save_processed
from loader import load

KAFKA_BOOTSTRAP = "localhost:9092"
TOPIC = "saramin-jobs-raw"
GROUP_ID = "etl-worker"


def _deserialize(v):
    """JSON 파싱 실패 시 None 반환 (ping 등 비JSON 메시지 무시)"""
    if not v:
        return None
    try:
        return json.loads(v.decode("utf-8"))
    except Exception:
        return None

# 마지막 메시지 수신 후 이 시간(초)이 지나면 배치 처리
FLUSH_SECONDS = 30
# 폴링 간격 (ms)
POLL_INTERVAL_MS = 5_000


def process_batch(records: list):
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 배치 처리 시작: {len(records)}건")
    df = pd.DataFrame(records)
    df = transform(df)
    log_data_quality(df)
    save_processed(df)
    load(df)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 배치 처리 완료\n")


def run():
    try:
        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            group_id=GROUP_ID,
            auto_offset_reset="earliest",   # 처음 실행 시 가장 오래된 메시지부터
            enable_auto_commit=True,
            value_deserializer=_deserialize,
        )
    except NoBrokersAvailable:
        raise RuntimeError(
            f"Kafka 브로커에 연결할 수 없습니다: {KAFKA_BOOTSTRAP}\n"
            "docker compose up -d 로 Kafka를 먼저 실행해주세요."
        )

    print(f"=== ETL Worker 대기 중 (topic={TOPIC}, group={GROUP_ID}) ===")

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
                print(f"메시지 누적: {len(batch)}건 (offset={msg.offset})")

            # 배치가 있고 FLUSH_SECONDS 이상 신규 메시지가 없으면 처리
            if batch and last_received_at:
                idle_seconds = (datetime.now() - last_received_at).seconds
                if idle_seconds >= FLUSH_SECONDS:
                    process_batch(batch)
                    batch = []
                    last_received_at = None

    except KeyboardInterrupt:
        print("\nETL Worker 종료 신호 수신")
    finally:
        if batch:
            print(f"종료 전 잔여 배치 처리: {len(batch)}건")
            process_batch(batch)
        consumer.close()
        print("ETL Worker 종료 완료")


if __name__ == "__main__":
    run()
