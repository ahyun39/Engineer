"""사람인 채용 공고 Load 모듈.

ETL 파이프라인의 Load 단계: transformer.py가 만든 가공 데이터를
Elasticsearch 인덱스에 bulk 적재한다.
job_id를 ES _id로 사용하므로 같은 공고를 재적재해도 중복되지 않는다.
"""

import math

import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from .config import ES_HOST, ES_INDEX
from .log_config import get_logger

logger = get_logger(__name__)

# career(원본), registered_at(원본), job_meta_count, error_msg 제외
LOAD_COLUMNS = [
    "job_id",
    "company_nm", "job_tit", "job_meta",
    "work_place", "city", "district",
    "career_level", "employment_type", "education",
    "salary", "salary_amount",
    "deadline", "deadline_date", "is_closed",
    "registered_at_dt", "crawl_time",
    "job_url", "source", "status",
]

MAPPING = {
    "mappings": {
        "properties": {
            "company_nm":      {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "job_tit":         {"type": "text"},
            "job_meta":        {"type": "keyword"},
            "work_place":      {"type": "keyword"},
            "city":            {"type": "keyword"},
            "district":        {"type": "keyword"},
            "career_level":    {"type": "keyword"},
            "employment_type": {"type": "keyword"},
            "education":       {"type": "keyword"},
            "salary":          {"type": "keyword"},
            "salary_amount":   {"type": "integer"},
            "deadline":        {"type": "keyword"},
            "deadline_date":   {"type": "date"},
            "is_closed":       {"type": "boolean"},
            "registered_at_dt": {"type": "date"},
            "crawl_time":      {"type": "date"},
            "job_url":         {"type": "keyword"},
            "source":          {"type": "keyword"},
            "status":          {"type": "keyword"},
        }
    }
}


def _get_client():
    return Elasticsearch(ES_HOST)


def _create_index_if_not_exists(es: Elasticsearch):
    if not es.indices.exists(index=ES_INDEX):
        es.indices.create(index=ES_INDEX, mappings=MAPPING["mappings"])
        logger.info("인덱스 생성: %s", ES_INDEX)


def _clean(v):
    """None/NaN 을 None으로 통일, 빈 리스트 제거"""
    if isinstance(v, list):
        return v if v else None
    if v is None:
        return None
    try:
        if isinstance(v, float) and math.isnan(v):
            return None
    except (TypeError, ValueError):
        pass
    return v


def _to_actions(df: pd.DataFrame):
    for record in df[LOAD_COLUMNS].to_dict(orient="records"):
        doc = {k: _clean(v) for k, v in record.items()}
        doc = {k: v for k, v in doc.items() if v is not None}

        job_id = doc.pop("job_id", None)
        if not job_id:
            continue

        yield {
            "_index": ES_INDEX,
            "_id": job_id,
            "_source": doc,
        }


def load(df: pd.DataFrame):
    es = _get_client()
    _create_index_if_not_exists(es)

    success, errors = bulk(es, _to_actions(df), raise_on_error=False)

    if errors:
        logger.error("ES 적재 실패 %d건: %s", len(errors), errors[:3])
    logger.info("ES 적재 완료: %d건 → index=%s", success, ES_INDEX)

    return success, errors


if __name__ == "__main__":
    import json
    import glob

    latest = sorted(glob.glob("data/processed/*.jsonl"))[-1]
    logger.info("적재 파일: %s", latest)

    records = [json.loads(line) for line in open(latest, encoding="utf-8")]
    df = pd.DataFrame(records)
    load(df)
