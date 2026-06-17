"""사람인 채용 공고 Extract 모듈.

ETL 파이프라인의 Extract 단계: 사람인 목록 페이지를 크롤링해
DataFrame으로 만들고, 원시 데이터를 JSON Lines로 저장한다.
이후 Kafka producer가 이 모듈의 결과를 토픽에 publish한다.
"""

import os
import re
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.saramin.co.kr"
LIST_URL = f"{BASE_URL}/zf_user/jobs/public/list/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")


def fetch_jobs_page(page):
    response = requests.get(
        LIST_URL,
        params={"page": page, "isAjaxRequest": "y"},
        headers=HEADERS,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    return soup.select("div.list_item")


def parse_job(item):
    company_nm = item.select_one(
        "div.company_nm .str_tit"
    ).get_text(strip=True)

    title_tag = item.select_one("div.job_tit .str_tit")
    job_tit = title_tag.get_text(strip=True)
    href = title_tag["href"]
    job_url = BASE_URL + href
    rec_idx = re.search(r"rec_idx=(\d+)", href).group(1)

    job_meta = [
        tag.get_text(strip=True)
        for tag in item.select("div.job_meta span.job_sector span")
    ]

    work_place = item.select_one("p.work_place").get_text(strip=True)
    career = item.select_one("p.career").get_text(strip=True)
    education = item.select_one("p.education").get_text(strip=True)
    salary = item.select_one("p.salary").get_text(strip=True)
    deadline = item.select_one("span.date").get_text(strip=True)
    registered_at = item.select_one("span.deadlines").get_text(strip=True)

    return {
        "job_id": rec_idx,
        "company_nm": company_nm,
        "job_tit": job_tit,
        "job_meta": job_meta,
        "job_meta_count": len(job_meta),
        "work_place": work_place,
        "career": career,
        "education": education,
        "salary": salary,
        "deadline": deadline,
        "registered_at": registered_at,
        "job_url": job_url,
        "source": "saramin",
        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:00:00"),
        "status": "success",
        "error_msg": None,
    }


def fallback_job_id(item):
    """파싱 실패 시에도 list_item의 id 속성(예: rec-12345678)에서 job_id를 복구"""
    raw_id = item.get("id", "")
    return raw_id.replace("rec-", "") or None


def build_error_record(item, error):
    return {
        "job_id": fallback_job_id(item),
        "company_nm": None,
        "job_tit": None,
        "job_meta": None,
        "job_meta_count": None,
        "work_place": None,
        "career": None,
        "education": None,
        "salary": None,
        "deadline": None,
        "registered_at": None,
        "job_url": None,
        "source": "saramin",
        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:00:00"),
        "status": "error",
        "error_msg": str(error),
    }


def scrape(pages=range(1, 11)):
    results = []

    for page in pages:
        print(f"크롤링 중: page={page}")
        jobs = fetch_jobs_page(page)
        print(f"공고 수: {len(jobs)}")

        for item in jobs:
            try:
                results.append(parse_job(item))
            except Exception as e:
                print(f"파싱 실패: {e}")
                results.append(build_error_record(item, e))

    df = pd.DataFrame(results)
    df = df.drop_duplicates(subset=["job_id"])
    return df


def save_raw(df, out_dir=RAW_DIR):
    os.makedirs(out_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, f"jobs_raw_{timestamp}.jsonl")

    df.to_json(path, orient="records", lines=True, force_ascii=False)

    print(f"원시 데이터 저장: {path} ({len(df)} rows)")
    return path


if __name__ == "__main__":
    df = scrape()
    print(
        f"총 수집 건수: {len(df)} "
        f"(성공: {(df['status'] == 'success').sum()}, "
        f"실패: {(df['status'] == 'error').sum()})"
    )
    save_raw(df)
