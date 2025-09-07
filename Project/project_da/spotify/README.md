!! need to replace deprecated api

# Spotify 기반 노래 추천 프로젝트

**요약**: 사용자가 입력한 조건(검색어 / 아티스트 / 플레이리스트 / 업로드된 트랙 리스트 / 사용자의 저장음원 등)에 해당하는 모든 트랙을 Spotify API로 수집하고 CSV로 저장한 뒤, 수집된 트랙의 메타데이터와 오디오 피처를 정교하게 분석하여 사용자의 요구사항에 가장 부합하는 상위 20곡을 추천하고 결과물을 저장/시각화하는 프로젝트입니다.

## 목차

1. 프로젝트 목표
2. 핵심 기능 요약
3. 아키텍처 및 데이터 흐름
4. 요구사항(환경, API 권한)
5. 설치 및 초기 세팅
6. 파일 구성
7. 코드 설명 — 핵심 스크립트 (fetch\_tracks.py, analyze\_and\_recommend.py, utils.py)
8. 실행 예시와 결과물
9. 추천 알고리즘 상세 (설계 근거, 수치화 방법)

## 1) 프로젝트 목표

* 사용자가 입력한 기준에 따라 Spotify에서 가능한 *모든* 관련 트랙을 수집한다.
* 트랙별 메타데이터(아티스트, 앨범, 발매일, 인기도 등)와 오디오 특성(tempo, energy, danceability 등)을 가져와 CSV로 저장한다.
* 저장된 데이터를 전처리 · 분석하여 사용자의 선호(명시적 가중치 또는 샘플 트랙)를 벡터로 만들고, 그에 가장 유사한 트랙 20곡을 선정하여 출력 및 CSV/HTML로 저장한다.
* 포트폴리오용으로 결과 요약(테이블, 시각화) HTML 파일을 생성한다.

## 2) 핵심 기능 요약

* 유연한 입력 방식: search query / artist / playlist / CSV of track IDs or names / current user's saved tracks
* 중복 제거, 아티스트/앨범 기반 중복 처리
* 오디오 피처 일괄 조회(최대 100개 배치 호출)
* 아티스트 장르 수집(가능한 경우)
* 추천: ① seed tracks 기반 추천 OR ② 가중치 기반 선호도 벡터 → 코사인 유사도 + popularity/recency 보정
* 결과물: `tracks_dump.csv`, `recommendations_top20.csv`, `recommendations_summary.html`

## 3) 아키텍처 및 데이터 흐름

1. 사용자 입력 → fetch\_tracks.py
2. Spotify Web API 호출 → raw track list + audio features
3. 데이터 정제 및 병합 → `tracks_dump.csv`
4. analyze\_and\_recommend.py 로 로드 → 피처 스케일링 + 선호도 벡터 구성
5. 유사도 계산 및 필터링 → top20 선정
6. 결과 출력 및 포트폴리오용 HTML 저장

## 4) 요구사항 (환경, API 권한)

* Python 3.9+
* Spotify 개발자 계정 ([https://developer.spotify.com)에서](https://developer.spotify.com%29에서) 앱 생성

  * Client ID, Client Secret 발급
  * Redirect URI 등록 (Authorization Code Flow 사용할 경우)
* 환경 변수 또는 `.env` 파일로 `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI` 설정
* 필요한 라이브러리: `spotipy`, `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `tqdm`, `python-dotenv`

## 5) 설치 및 초기 세팅

```bash
# 가상환경 생성 권장
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 6) 파일 구성

```
spotify_recommender/
├─ README.md
├─ requirements.txt
├─ .env
├─ fetch_tracks.py          # Spotify에서 트랙 수집, CSV 저장
├─ analyze_and_recommend.py# 추천 로직 및 결과물 생성
├─ utils.py                 # 공통 헬퍼 (페이지네이션, 배치 요청, 캐시)
├─ notebooks/
│  └─ exploratory_analysis.ipynb
├─ streamlit_app.py         # (선택) 실시간 UI 데모
└─ outputs/
   ├─ tracks_dump.csv
   ├─ recommendations_top20.csv
   └─ recommendations_summary.html
```