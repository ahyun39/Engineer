from datetime import datetime, date, timedelta

from src.transformer import (
    parse_deadline,
    parse_registered_at,
    is_deadline_closed,
    clean_company_nm,
    split_career,
    parse_salary_amount,
    split_work_place,
)

REF = datetime(2025, 6, 15, 10, 0, 0)  # 기준 시각


# parse_deadline
def test_parse_deadline_tomorrow():
    assert parse_deadline("내일마감", REF) == date(2025, 6, 16)

def test_parse_deadline_today():
    assert parse_deadline("오늘마감", REF) == date(2025, 6, 15)

def test_parse_deadline_dday():
    assert parse_deadline("D-3", REF) == date(2025, 6, 18)

def test_parse_deadline_date_format():
    assert parse_deadline("06.30(월)", REF) == date(2025, 6, 30)

def test_parse_deadline_unknown_returns_none():
    assert parse_deadline("상시채용", REF) is None

def test_parse_deadline_none_input():
    assert parse_deadline(None, REF) is None


# parse_registered_at
def test_parse_registered_at_minutes():
    assert parse_registered_at("30분 전", REF) == REF - timedelta(minutes=30)

def test_parse_registered_at_hours():
    assert parse_registered_at("2시간 전", REF) == REF - timedelta(hours=2)

def test_parse_registered_at_days():
    assert parse_registered_at("3일 전", REF) == REF - timedelta(days=3)

def test_parse_registered_at_none_input():
    assert parse_registered_at(None, REF) is None


# is_deadline_closed
def test_is_deadline_closed_past():
    assert is_deadline_closed("06.14", date(2025, 6, 14), REF) is True

def test_is_deadline_closed_future():
    assert is_deadline_closed("06.30", date(2025, 6, 30), REF) is False

def test_is_deadline_closed_hour_passed():
    # "09시 마감", 기준 시각이 10시 → 마감됨
    assert is_deadline_closed("09시 마감", date(2025, 6, 15), REF) is True

def test_is_deadline_closed_hour_not_yet():
    # "12시 마감", 기준 시각이 10시 → 아직 유효
    assert is_deadline_closed("12시 마감", date(2025, 6, 15), REF) is False

def test_is_deadline_closed_no_date():
    assert is_deadline_closed(None, None, REF) is False


# clean_company_nm
def test_clean_company_nm_parenthesis():
    assert clean_company_nm("(주)카카오") == "카카오"

def test_clean_company_nm_kakao_symbol():
    assert clean_company_nm("㈜네이버") == "네이버"

def test_clean_company_nm_none():
    assert clean_company_nm(None) is None


# split_career
def test_split_career_new_and_fulltime():
    levels, types = split_career("신입 · 정규직")
    assert levels == ["신입"]
    assert types == ["정규직"]

def test_split_career_experienced():
    levels, types = split_career("경력 · 계약직")
    assert levels == ["경력"]
    assert types == ["계약직"]

def test_split_career_none():
    assert split_career(None) == (None, None)


# parse_salary_amount
def test_parse_salary_amount_with_comma():
    assert parse_salary_amount("3,000만원") == 30_000_000

def test_parse_salary_amount_negotiable():
    assert parse_salary_amount("협의") == 0

def test_parse_salary_amount_none():
    assert parse_salary_amount(None) == 0


# split_work_place
def test_split_work_place_city_district():
    city, district = split_work_place("서울 강남구")
    assert city == "서울"
    assert district == "강남구"

def test_split_work_place_all_district():
    city, district = split_work_place("서울전체")
    assert city == "서울"
    assert district == "전체"

def test_split_work_place_none():
    assert split_work_place(None) == (None, None)
