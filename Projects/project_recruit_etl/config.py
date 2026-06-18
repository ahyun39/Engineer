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
FLUSH_SECONDS:    int = int(os.getenv("FLUSH_SECONDS",    "30"))
POLL_INTERVAL_MS: int = int(os.getenv("POLL_INTERVAL_MS", "5000"))

# Elasticsearch
ES_HOST:  str = os.getenv("ES_HOST",  "http://localhost:9200")
ES_INDEX: str = os.getenv("ES_INDEX", "saramin-jobs")

# Scraper
SARAMIN_BASE_URL: str = os.getenv("SARAMIN_BASE_URL", "https://www.saramin.co.kr")
SCRAPE_PAGES:     int = int(os.getenv("SCRAPE_PAGES", "10"))
