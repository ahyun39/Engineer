"""파이프라인 설정.

.env 파일에서 환경변수를 읽어 모듈 상수로 제공한다.
환경변수가 없으면 기본값을 사용하므로 .env 없이도 로컬에서 바로 실행 가능하다.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# Kafka
KAFKA_BOOTSTRAP: str = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
KAFKA_TOPIC: str     = os.getenv("KAFKA_TOPIC",     "saramin-jobs-raw")
KAFKA_GROUP_ID: str  = os.getenv("KAFKA_GROUP_ID",  "etl-worker")

# ETL Worker 튜닝
FLUSH_SECONDS:        int = int(os.getenv("FLUSH_SECONDS",        "30"))
POLL_INTERVAL_MS:     int = int(os.getenv("POLL_INTERVAL_MS",     "5000"))
DATA_RETENTION_DAYS:  int = int(os.getenv("DATA_RETENTION_DAYS",  "7"))

# Elasticsearch
ES_HOST:  str = os.getenv("ES_HOST",  "http://localhost:9200")
ES_INDEX: str = os.getenv("ES_INDEX", "saramin-jobs")

# Scraper (크롤러 — 메인 Extract 경로)
SARAMIN_BASE_URL: str = os.getenv("SARAMIN_BASE_URL", "https://www.saramin.co.kr")
SCRAPE_PAGES:     int = int(os.getenv("SCRAPE_PAGES", "10"))

# 사람인 공식 API (api_extractor.py — 대안 Extract 경로, API 키 있을 때만 사용)
SARAMIN_API_KEY:   str = os.getenv("SARAMIN_API_KEY",   "")
SARAMIN_API_COUNT: int = int(os.getenv("SARAMIN_API_COUNT", "110"))   # 요청당 최대 110건
SARAMIN_API_PAGES: int = int(os.getenv("SARAMIN_API_PAGES", "1"))