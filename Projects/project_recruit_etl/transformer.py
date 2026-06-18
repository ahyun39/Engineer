"""사람인 채용 공고 Transform 모듈.

ETL 파이프라인의 Transform 단계: scraper.py가 만든 원시 데이터를
분석 가능한 형태로 정제/표준화하고, 가공 데이터를 JSON Lines로 저장한다.
이후 ETL Worker가 이 모듈을 호출해 Elasticsearch에 적재(Load)하게 된다.
"""

import os
import re
from datetime import datetime, timedelta

import pandas as pd

from log_config import get_logger

logger = get_logger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

CAREER_LEVELS = {"신입", "경력", "경력무관"}


def parse_deadline(deadline_text, reference_dt):
    if pd.isna(deadline_text):
        return None

    text = deadline_text.strip()

    if "내일마감" in text:
        return (reference_dt + timedelta(days=1)).date()

    if "오늘마감" in text or re.search(r"\d{1,2}시\s*마감", text):
        return reference_dt.date()

    m = re.match(r"D-(\d+)", text)
    if m:
        return (reference_dt + timedelta(days=int(m.group(1)))).date()

    m = re.search(r"(\d{1,2})\.(\d{1,2})", text)
    if m:
        month, day = int(m.group(1)), int(m.group(2))
        deadline_date = datetime(reference_dt.year, month, day).date()

        # 12월 공고가 1월로 넘어가는 경우 등, 과거 날짜로 계산되면 다음 해로 보정
        if deadline_date < reference_dt.date():
            deadline_date = datetime(reference_dt.year + 1, month, day).date()

        return deadline_date

    # "상시채용" 등 패턴에 안 걸리는 표기는 결측으로 남긴다
    return None


def parse_registered_at(registered_text, reference_dt):
    if pd.isna(registered_text):
        return None

    text = registered_text.strip()

    m = re.match(r"(\d+)분 전", text)
    if m:
        return reference_dt - timedelta(minutes=int(m.group(1)))

    m = re.match(r"(\d+)시간 전", text)
    if m:
        return reference_dt - timedelta(hours=int(m.group(1)))

    m = re.match(r"(\d+)일 전", text)
    if m:
        return reference_dt - timedelta(days=int(m.group(1)))

    return None


def is_deadline_closed(deadline_text, deadline_date, reference_dt):
    if deadline_date is None:
        return False

    if not pd.isna(deadline_text):
        m = re.search(r"(\d{1,2})시\s*마감", deadline_text)
        if m:
            deadline_hour = int(m.group(1))
            # "HH시 마감"은 크롤링 당일 마감이므로, 날짜가 같을 때만 시(hour)로 마감 여부를 따진다
            return reference_dt.date() == deadline_date and reference_dt.hour >= deadline_hour

    return deadline_date < reference_dt.date()


def clean_company_nm(text):
    if pd.isna(text):
        return None

    text = re.sub(r"\([^)]*\)", "", text)
    text = text.replace("㈜", "")

    return text.strip()


def clean_work_place(text):
    if pd.isna(text):
        return None

    return re.sub(r"\s*외$", "", text).strip()


def clean_education(text):
    if pd.isna(text):
        return None

    text = text.replace("↑", "이상")
    text = text.replace("대학(2,3년)이상", "초대졸이상")
    text = text.replace("대학교(4년)이상", "대졸이상")

    return text


def split_career(text):
    if pd.isna(text):
        return None, None

    tokens = text.split(" · ")
    levels = [t for t in tokens if t in CAREER_LEVELS]
    types = [t for t in tokens if t not in CAREER_LEVELS]

    career_level = levels if levels else None
    employment_type = types if types else None

    return career_level, employment_type


def parse_salary_amount(text):
    if pd.isna(text):
        return 0

    m = re.search(r"([\d,]+)\s*만원", text)
    if not m:
        return 0

    return int(m.group(1).replace(",", "")) * 10000


def split_work_place(text):
    if pd.isna(text):
        return None, None

    if "전체" in text and " " not in text:
        return text.replace("전체", ""), "전체"

    tokens = text.split(" ", 1)
    city = tokens[0]
    district = tokens[1] if len(tokens) > 1 else None

    return city, district


def transform(df):
    df = df.copy()
    df["crawl_time"] = pd.to_datetime(df["crawl_time"])

    df["deadline_date"] = df.apply(
        lambda row: parse_deadline(row["deadline"], row["crawl_time"]),
        axis=1
    )

    df["registered_at_dt"] = df.apply(
        lambda row: parse_registered_at(row["registered_at"], row["crawl_time"]),
        axis=1
    )

    df["company_nm"] = df["company_nm"].apply(clean_company_nm)
    df["work_place"] = df["work_place"].apply(clean_work_place)
    df["education"] = df["education"].apply(clean_education)

    df["is_closed"] = df.apply(
        lambda row: is_deadline_closed(row["deadline"], row["deadline_date"], row["crawl_time"]),
        axis=1
    )

    df[["career_level", "employment_type"]] = df["career"].apply(
        lambda x: pd.Series(split_career(x))
    )

    df["salary_amount"] = df["salary"].apply(parse_salary_amount)

    df[["city", "district"]] = df["work_place"].apply(
        lambda x: pd.Series(split_work_place(x))
    )

    return df


def log_data_quality(df: pd.DataFrame) -> None:
    logger.info("=== 컬럼별 결측치 개수 ===\n%s", df.isna().sum().to_string())

    salary_anomaly_cnt = int(
        ((df["salary_amount"] == 0) & (~df["salary"].str.contains("협의|채용시", na=False))).sum()
    )
    career_null   = int(df["career_level"].isna().sum())
    emp_null      = int(df["employment_type"].isna().sum())
    district_null = int(df["district"].isna().sum())

    # 이상치는 WARNING, 정상(0건)은 INFO
    (logger.warning if salary_anomaly_cnt > 0 else logger.info)(
        "salary_amount=0 인데 협의류 표현 아닌 행: %d건", salary_anomaly_cnt
    )
    (logger.warning if career_null > 0 else logger.info)(
        "career_level 분리 실패: %d건", career_null
    )
    (logger.warning if emp_null > 0 else logger.info)(
        "employment_type 분리 실패: %d건", emp_null
    )
    (logger.warning if district_null > 0 else logger.info)(
        "district 분리 실패: %d건", district_null
    )


def save_processed(df, out_dir=PROCESSED_DIR):
    os.makedirs(out_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, f"jobs_processed_{timestamp}.jsonl")

    df.to_json(path, orient="records", lines=True, force_ascii=False, date_format="iso")

    logger.info("가공 데이터 저장: %s (%d rows)", path, len(df))
    return path


if __name__ == "__main__":
    from scraper import scrape

    raw_df = scrape()
    processed_df = transform(raw_df)
    log_data_quality(processed_df)
    save_processed(processed_df)
