"""사람인 채용 공고 Extract — 공식 API 기반 (대안 Extract 경로).

사람인 채용정보 Open API를 사용해 공고를 수집하고 DataFrame으로 반환한다.
반환 스키마는 scraper.py와 동일하므로 이후 Transform 단계가
크롤러/API 구분 없이 동작한다. 메인 파이프라인은 scraper.py 기반이며,
이 모듈은 API 키가 있을 때 선택적으로 사용할 수 있는 대안 경로다.

사전 준비:
    https://oapi.saramin.co.kr 에서 API 키 발급 후 .env에 SARAMIN_API_KEY 설정

실행:
    python -m src.api_extractor
"""

from datetime import datetime

import pandas as pd
import requests

from .config import SARAMIN_API_KEY, SARAMIN_API_COUNT, SARAMIN_API_PAGES
from .scraper import save_raw
from .log_config import get_logger

logger = get_logger(__name__)

_API_URL = "https://oapi.saramin.co.kr/job-search"


def _fetch(start: int) -> list[dict]:
    params = {
        "access-key": SARAMIN_API_KEY,
        "count": SARAMIN_API_COUNT,
        "start": start,
        "fields": "salary",
        "_type": "json",
    }
    resp = requests.get(_API_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json().get("jobs", {}).get("job", [])


def _parse(job: dict) -> dict:
    pos = job.get("position", {})
    now = datetime.now()

    # 경력·고용형태: "신입 · 정규직" 형식으로 재조합 (transformer.split_career 호환)
    career_level = pos.get("experience-level", {}).get("name", "")
    job_type     = pos.get("job-type",         {}).get("name", "")
    career = " · ".join(filter(None, [career_level, job_type]))

    # 마감일: ISO → "MM.DD" (transformer.parse_deadline MM.DD 분기 호환)
    exp_date = job.get("expiration-date", "")
    try:
        deadline = datetime.strptime(exp_date, "%Y-%m-%d").strftime("%m.%d")
    except ValueError:
        deadline = exp_date

    # 등록일: ISO → "N일 전" (transformer.parse_registered_at 호환)
    post_date = job.get("posting-date", "")
    try:
        days_ago = (now.date() - datetime.strptime(post_date, "%Y-%m-%d").date()).days
        registered_at = f"{days_ago}일 전" if days_ago >= 0 else post_date
    except ValueError:
        registered_at = post_date

    industry = pos.get("industry", {}).get("name", "")

    return {
        "job_id":         str(job.get("id", "")),
        "company_nm":     job.get("company", {}).get("detail", {}).get("name", ""),
        "job_tit":        pos.get("title", ""),
        "job_meta":       [industry] if industry else [],
        "job_meta_count": 1 if industry else 0,
        "work_place":     pos.get("location", {}).get("name", ""),
        "career":         career,
        "education":      pos.get("required-education-level", {}).get("name", ""),
        "salary":         job.get("salary", {}).get("name", ""),
        "deadline":       deadline,
        "registered_at":  registered_at,
        "job_url":        job.get("url", ""),
        "source":         "saramin_api",
        "crawl_time":     now.strftime("%Y-%m-%d %H:00:00"),
        "status":         "success",
        "error_msg":      None,
    }


def extract(pages: int = SARAMIN_API_PAGES) -> pd.DataFrame:
    """사람인 API에서 채용 공고를 수집해 DataFrame으로 반환한다."""
    if not SARAMIN_API_KEY:
        raise RuntimeError("SARAMIN_API_KEY가 설정되지 않았습니다. .env를 확인해주세요.")

    records = []

    for page in range(pages):
        start = page * SARAMIN_API_COUNT
        logger.debug("API 요청: page=%d, start=%d", page + 1, start)
        try:
            jobs = _fetch(start)
        except Exception as e:
            logger.error("API 요청 실패: page=%d, %s", page + 1, e)
            break

        if not jobs:
            logger.info("데이터 없음: page=%d에서 중단", page + 1)
            break

        records.extend(_parse(j) for j in jobs)
        logger.debug("수집: %d건 (누적 %d건)", len(jobs), len(records))

    if not records:
        logger.warning("API 수집 결과 없음")
        return pd.DataFrame()

    df = pd.DataFrame(records).drop_duplicates(subset=["job_id"])
    logger.info("API 수집 완료: %d건", len(df))   # _parse는 항상 success 레코드만 생성
    return df


if __name__ == "__main__":
    df = extract()
    save_raw(df)
