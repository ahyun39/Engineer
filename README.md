# Engineer

데이터 엔지니어링, 머신러닝, LLM/RAG, 시스템 설계 학습 및 프로젝트 내용

---

## 📁 Repository Structure

```
Engineer/
├── Data_Engineering/       # 데이터 엔지니어링 이론 및 실습
├── LLM_RAG/                # LLM 및 RAG 파이프라인 구현
├── Machine_Learning/       # 머신러닝·딥러닝 이론 및 실습
├── Projects/               # 데이터 분석 및 ML 프로젝트
├── Python/                 # Python 프레임워크 학습
└── System_Design/          # 시스템 설계 이론
```

---

## Data_Engineering

데이터베이스 이론부터 웹 크롤링까지 데이터 수집·저장·처리

| 디렉토리 | 내용 |
|---|---|
| `Database/` | DB 개념, 데이터 모델링, 정규화, SQL vs NoSQL |
| `Data_Warehouse/` | 데이터 웨어하우스 구조, ETL 파이프라인 |
| `web_crawling/` | Selenium/BeautifulSoup 크롤링, 멜론 차트 수집 |

---

## LLM_RAG

LLM 아키텍처 이해부터 실제 RAG 애플리케이션 구현

| 디렉토리 | 내용 |
|---|---|
| `LLM/` | Transformer 아키텍처, HuggingFace Transformers 실습 |
| `RAG/llm-application/` | LangChain + Chroma/Pinecone RAG 구현 (6개 실습 노트북) |
| `RAG/streamlit/` | RAG 기반 Streamlit 챗봇 애플리케이션 |

**주요 실습:**
- LangChain + Chroma를 활용한 기본 RAG 구성
- Upstage Embeddings 통합
- Pinecone 벡터 DB 연동
- Retrieval 효율 개선을 위한 데이터 전처리

---

## Machine_Learning

머신러닝·딥러닝·강화학습 이론 및 실습

| 디렉토리 | 내용 |
|---|---|
| `Deep_Learning/` | 퍼셉트론, 활성화 함수 구현 및 실습 |
| `Reinforcement_Learning/` | 강화학습 개념, MDP, 벨만 방정식 |
| `Studies/` | 기초 ML 실습 (Iris 데이터셋 분석) |

---

## Projects

실제 데이터를 활용한 분석 및 모델링 프로젝트

### 완성 프로젝트

| 프로젝트 | 설명 |
|---|---|
| `project_movie_recommend/` | 영화·애니메이션 추천 시스템 (Laftel, MAL, MovieLens 데이터) |
| `project_Recommendation/` | 매장 추천 시스템 (FastAPI 서빙 포함) |
| `project_recycle_chatbot/` | 분리수거 안내 RAG 챗봇 |
| `project_KOSIS_library/` | KOSIS API 기반 국립도서관 데이터 분석 |

### 인턴십 프로젝트

| 프로젝트 | 설명 |
|---|---|
| `Intern/Data_Standardization/` | 메타데이터 표준화 및 AI 활용 방안 연구 |
| `Intern/Law_data_analysis_RAG/` | RAG를 위한 법령 데이터 청킹 로직 설계 및 분석 |

### Archive

미완성 또는 학습 목적 프로젝트

| 프로젝트 | 설명 |
|---|---|
| `(dev_course)_project_baseball/` | 야구 데이터 EDA (수강 과제) |
| `(temp)_project_da_music/` | AI Hub 음악 데이터 EDA |
| `(temp)_ranking_agent/` | 코스메 브랜드 랭킹 크롤링 및 데이터 증강 |

---

## Python

Python 주요 프레임워크와 테스트 도구

| 디렉토리 | 내용 |
|---|---|
| `Django/` | Django MVC 패턴, View·Template·Model·Form |
| `Pytest/` | Pytest 기본 사용법, fixtures, parametrize, xfail, skip |

---

## System_Design

대규모 시스템 설계 방법론과 아키텍처 패턴

| 디렉토리/파일 | 내용 |
|---|---|
| `MSA/` | 마이크로서비스 아키텍처, Agile/Scrum, Netflix MSA 사례 |
| `시스템_디자인_설계/` | 요구사항 분석 → 용량 추정 → API 설계 → 핵심 문제 해결 단계별 방법론 |
| `CI_CD.md` | CI/CD 파이프라인 개념 및 구성 |
