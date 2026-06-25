# 포트폴리오 리뷰 — project_recruit_etl

> 리뷰어: 10년차 시니어 데이터 엔지니어 관점  
> 대상: 신입 데이터 엔지니어 지원자 포트폴리오  
> 리뷰 기준일: 2026-06-25 (현재 src/ 구조 기준)

---

## 종합 평가

**B+ / 신입 기준 상위 10~15%**

단순 CRUD 앱이나 튜토리얼 따라하기가 아닙니다. 실제 분산 파이프라인을 설계하고 E2E로 완성했습니다. 크롤링 → Kafka → ETL → Elasticsearch → Kibana 전 단계를 한 명이 구현하고, logging 설계, 환경변수 분리, 단위 테스트, 문서화까지 갖췄습니다. 신입 포트폴리오에서 이 조합을 완성한 사례는 드뭅니다.

단, 코드를 실제로 읽어보면 **한 가지 구조 문제가 즉시 눈에 들어옵니다**. 이것만 해결하면 서류 통과 수준은 충분합니다.

---

## 잘된 점 — 구체적으로

### 1. 전체 파이프라인을 직접 설계했다

```
kafka_producer.py → Kafka → etl_worker.py → transformer.py → loader.py → ES → Kibana
```

각 단계가 파일 단위로 분리되어 있고 역할이 명확합니다. "ETL을 해봤다"와 "ETL 파이프라인을 설계했다"는 다릅니다. 이 프로젝트는 후자입니다.

### 2. 멱등 적재 설계

`job_id`를 ES `_id`로 사용해 하루 2번 수집해도 중복 문서가 생기지 않습니다.

```python
yield {
    "_index": ES_INDEX,
    "_id": job_id,       # 같은 job_id로 재색인 → upsert
    "_source": doc,
}
```

배치 파이프라인에서 idempotency는 운영 필수 조건입니다. ES의 upsert 특성으로 자연스럽게 해결한 판단이 좋습니다.

### 3. Kafka offset 수동 커밋

```python
# etl_worker.py
enable_auto_commit=False,   # 수동 커밋: process_batch 완료 후에만 커밋
...
process_batch(batch)
consumer.commit()           # 처리 완료 후 커밋
```

`enable_auto_commit=True`로 두면 `process_batch()` 실행 중 프로세스가 죽었을 때 데이터가 유실됩니다. 이걸 수동 커밋으로 해결한 코드는 "Kafka를 이해하고 썼다"는 증거입니다. 면접에서 반드시 설명하세요.

### 4. Graceful Shutdown

```python
except KeyboardInterrupt:
    logger.info("ETL Worker 종료 신호 수신")
finally:
    if batch:
        logger.info("종료 전 잔여 배치 처리: %d건", len(batch))
        process_batch(batch)
        consumer.commit()
    consumer.close()
```

Ctrl+C를 눌렀을 때 남은 배치를 처리하고 Consumer를 정상 종료합니다. 이 패턴 없이 프로세스를 죽이면 처리 중인 데이터가 사라집니다. 여기까지 신경 쓴 신입은 많지 않습니다.

### 5. logging 설계 수준

```python
# log_config.py
TimedRotatingFileHandler(when="midnight", backupCount=7)  # 자정 로테이션, 7일 보관
ch.setLevel(logging.INFO)   # 콘솔: INFO 이상
fh.setLevel(logging.DEBUG)  # 파일: DEBUG 이상 전부
```

중앙 설정 모듈 하나에서 관리하고, 콘솔과 파일의 레벨을 다르게 설정했습니다. `%s` 스타일 포맷팅으로 꺼진 레벨의 문자열 생성을 건너뜁니다. `transformer.py`의 이상치 레벨 동적 결정 패턴도 실무 수준입니다.

```python
(logger.warning if salary_anomaly_cnt > 0 else logger.info)(
    "salary_amount=0 인데 협의류 표현 아닌 행: %d건", salary_anomaly_cnt
)
```

### 6. 환경변수 분리

`config.py` + `.env` + `.env.example` 구조. `os.getenv(key, default)` 패턴으로 `.env` 없이도 로컬 실행 가능. `.env.example`을 커밋해 온보딩 맥락 제공. 교과서적으로 맞습니다.

### 7. 단위 테스트 품질

`tests/test_transformer.py` 27개 케이스. 주목할 부분:

- `REF = datetime(2025, 6, 15, 10, 0, 0)` — 기준 시각을 고정해 날짜 의존성 제거
- `is_deadline_closed`: 시(hour) 기반 마감 처리를 실제로 검증
- `parse_deadline`: D-N, 오늘마감, 내일마감, MM.DD, 상시채용 5개 분기 전부 커버
- `None` 입력 케이스를 빠짐없이 테스트

엣지 케이스를 직접 떠올리고 테스트했다는 게 보입니다.

### 8. 크롤러 + 공식 API 이중 구현

`scraper.py`(HTML 크롤링)와 `api_extractor.py`(공식 API) 두 가지 Extract 방식을 구현하고, 두 출력의 스키마를 통일해 이후 Transform이 구분 없이 동작하도록 설계했습니다. 유지보수와 확장성을 함께 고려한 판단입니다.

### 9. Docker Compose healthcheck + KRaft 모드

```yaml
healthcheck:
  test: ["CMD", "curl", "-sf", "http://localhost:9200"]
depends_on:
  elasticsearch:
    condition: service_healthy   # ES 준비 전에 Kibana가 뜨는 문제 방지
```

`depends_on`만 쓰면 컨테이너가 시작됐는지만 확인합니다. `service_healthy`는 실제 서비스 준비까지 기다립니다. Kafka를 Zookeeper 없는 KRaft 모드로 구성한 것도 최신 트렌드에 맞습니다.

### 10. 문서화

README(아키텍처 다이어그램, 스키마, 실행 방법, 보안 설명), `study_notes.md`(개념 정리), `record.ipynb`(개발 과정). 이 수준으로 문서를 갖춘 신입 포트폴리오는 거의 없습니다. "문서를 쓸 줄 아는 엔지니어"라는 인상을 줍니다.

---

## 개선이 필요한 부분

### ✅ HIGH — 해결 완료

#### 1. ~~import 경로가 실행 위치에 종속되어 있음~~ → 수정 완료

`src/` 내부 모든 파일을 상대 import로 전환하고, `src/__init__.py`를 추가해 패키지로 만들었습니다.

```python
# 수정 전 (절대경로 — 특정 디렉토리에서만 동작)
from Projects.project_recruit_etl.src.config import SARAMIN_BASE_URL

# 수정 후 (상대 import — 패키지 내부 어디서든 동작)
from .config import SARAMIN_BASE_URL
```

`log_config.py`, `scraper.py`, `transformer.py`의 `BASE_DIR`도 `src/` 내부를 가리키던 문제를 수정했습니다.

```python
# 수정 전: src/ 내부를 가리킴 → logs/, data/ 경로 오류
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 수정 후: 프로젝트 루트를 가리킴
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

`api_extractor.py`(루트)는 `from src.X import Y` 방식, `tests/`는 `from src.X import Y` 방식으로 통일했습니다.

`src/config.py`에 누락되어 있던 API 설정(`SARAMIN_API_KEY`, `SARAMIN_API_COUNT`, `SARAMIN_API_PAGES`)도 추가했습니다.

**실행 방법 (프로젝트 루트에서):**

```bash
python -m src.etl_worker
python -m src.kafka_producer
pytest tests/
```

README와 crontab 예시도 `-m src.X` 방식으로 수정했습니다.

#### 2. process_batch에 예외 처리가 없음

```python
def process_batch(records: list):
    df = pd.DataFrame(records)
    df = transform(df)      # 예외 발생 시?
    log_data_quality(df)
    save_processed(df)
    load(df)                # ES 다운 시?
```

`transform()`이나 `load()` 중간에 예외가 발생하면 `process_batch()`가 터지고, `finally` 블록에서 `consumer.commit()`이 호출되지 않습니다. 수동 커밋 설계가 좋았는데, 예외 처리가 없어서 구멍이 생깁니다.

```python
# 최소한 이 정도는 필요
def process_batch(records: list):
    try:
        df = pd.DataFrame(records)
        df = transform(df)
        log_data_quality(df)
        save_processed(df)
        load(df)
    except Exception as e:
        logger.error("배치 처리 실패 — 데이터 유실 가능: %s", e, exc_info=True)
        raise  # 상위로 전파해 commit을 건너뛰게 함
```

---

### 🟡 MEDIUM — 면접에서 알고 있어야 할 한계

#### 3. rate limiting 없는 크롤러

```python
for page in pages:
    logger.debug("크롤링 중: page=%d", page)
    jobs = fetch_jobs_page(page)  # 딜레이 없이 연속 요청
```

10페이지를 딜레이 없이 요청합니다. 실무에서는 대상 서비스의 이용약관 확인과 robots.txt 준수가 선행되어야 합니다. 사람인은 공식 채용정보 API를 제공하고 있고 (`api_extractor.py`에 구현), 포트폴리오 목적의 소량 수집임을 README에 명시하는 것이 좋습니다.

> **면접 예상 질문**: "사람인 크롤링 시 rate limit이나 이용약관은 확인하셨나요?"

#### 4. crontab 단독 스케줄링의 한계

```cron
0 11 * * * python kafka_producer.py >> logs/cron.log 2>&1
```

실패해도 알림 없음, 재시도 없음, 이전 실행이 끝나지 않아도 다음 실행을 막지 않습니다. 실무에서는 최소 Slack webhook 알림이라도 있어야 합니다.

> **면접 예상 질문**: "배치가 실패하면 어떻게 알 수 있나요? 11시 배치가 늦게 끝나면 18시 배치가 겹치지 않나요?"

#### 5. 빈 배치 처리 없음

`scrape()`가 0건을 반환하면 Kafka에 0건이 발행됩니다. Consumer 측에서 `process_batch([])`가 호출되면 빈 DataFrame으로 transform/load가 실행됩니다. 명시적 가드가 없습니다.

```python
def process_batch(records: list):
    if not records:
        logger.warning("빈 배치 수신, 처리 건너뜀")
        return
    ...
```

---

### 🟢 LOW — 알면 더 좋은 것들

#### 6. 테스트 커버리지 편중

`transformer.py`만 테스트됩니다. 다음도 단위 테스트가 가능합니다.

- `scraper.py`: HTML fixture 파일로 `parse_job()` 테스트 (실제 HTTP 요청 없이)
- `loader.py`: `_to_actions()` 로직 검증 (ES 클라이언트 mock)
- `api_extractor.py`: API 응답 fixture로 `_parse()` 테스트

#### 7. 타입 힌트 일관성

`log_config.py`, `loader.py`에는 타입 힌트가 있지만 `scraper.py`의 함수들에는 없습니다.

```python
def fetch_jobs_page(page):       # 타입 없음
def parse_job(item):             # 타입 없음

def load(df: pd.DataFrame):      # 있음
def get_logger(name: str) -> logging.Logger:  # 있음
```

#### 8. 로그 파일이 하나

모든 모듈이 `pipeline.log`를 공유합니다. 배치가 쌓이면 scraper 디버깅 시 worker 로그가 섞여 찾기 어렵습니다.

#### 9. git에 불필요한 파일이 추적됨

루트에 `__pycache__/`가 남아있습니다 (src/ 이전 구조 잔재). `data/`와 `logs/` 디렉토리의 실제 데이터 파일(.jsonl, .log)도 git에 커밋되어 있을 수 있습니다. `.gitignore`에 추가하고 이미 커밋된 파일은 `git rm --cached`로 정리하는 것이 좋습니다.

---

## 면접 예상 질문 & 준비 포인트

| 질문 | 핵심 답변 포인트 |
|------|----------------|
| "Kafka를 왜 썼나요? ES에 바로 넣으면 안 되나요?" | Producer/Consumer 분리로 크롤링 실패가 적재에 영향 없음. ES 다운 시 메시지 Kafka에 보관 후 재처리 가능. 추후 Consumer를 추가해 ML 파이프라인 등 다목적 활용 가능. |
| "enable_auto_commit=False로 설정하셨는데, 그 의미는?" | auto_commit은 poll 시점에 offset 커밋 → process_batch 실패 시 데이터 유실. 수동 커밋은 process_batch 완료 후에만 커밋 → at-least-once 보장. 단, commit 전에 죽으면 중복 처리 가능. ES upsert로 최종 적재는 멱등. |
| "Consumer가 재시작되면 어떻게 되나요?" | `auto_offset_reset=earliest`로 미커밋 메시지부터 재처리. ES upsert로 중복 적재 없음. JSONL 파일 중복은 한계. |
| "xpack.security를 왜 끄셨나요?" | 로컬 단일 노드, localhost 접근만 있음. 운영 전환 시 `elastic` 계정 설정, loader.py에 `basic_auth` 추가, ES_HOST를 https로 변경. README에 절차 명시. |
| "배치가 실패하면 어떻게 알 수 있나요?" | 현재는 로그 확인뿐. 개선 방향은 실패 시 Slack webhook 알림, 또는 Airflow 같은 워크플로우 도구 도입. |
| "크롤링 관련 법적 검토는 하셨나요?" | 포트폴리오 목적으로 소량 수집. 공식 API를 api_extractor.py로 병행 구현. 실무에서는 robots.txt 확인, 이용약관 검토, 공식 API 우선 사용이 원칙. |
| "Logstash는 왜 안 썼나요?" | 복잡한 날짜 파싱(parse_deadline, parse_registered_at)과 비즈니스 로직을 Python으로 자유롭게 구현하기 위해. Logstash DSL로는 이 수준의 변환 로직 구현이 어려움. Kafka를 중간에 두어 장애 격리도 확보. |
| "FLUSH_SECONDS=30은 어떤 기준으로?" | 사람인 10페이지 크롤링 소요 시간(약 10~15초) 기준으로 여유 있게 설정. 조정이 필요하면 .env에서 변경 가능. |

---

## 제출 가능 여부

**지금 당장 제출 가능한 수준이다. 다만 process_batch 예외 처리 하나가 남아있다.**

```
현재 코드베이스 완성도
├── ✅ 전체 E2E 파이프라인 (Kafka + ES + Kibana)
├── ✅ KRaft 모드, 멱등 적재, Graceful Shutdown
├── ✅ logging 설계, 환경변수 분리
├── ✅ 단위 테스트 27개, 문서화
├── ✅ 수동 Kafka 커밋, healthcheck
├── ✅ 크롤러 + 공식 API 이중 구현
├── ✅ import 경로 수정 완료 (상대 import + python -m src.X)
├── ⚠️  process_batch 예외 처리 → 수정 필요
└── ℹ️  rate limiting, crontab 알림 → 면접에서 "알고 있는 한계"로 설명
```

신입 포트폴리오에서 "다 완벽합니다"보다 "이 부분은 이런 한계가 있고, 실무에서는 이렇게 개선해야 합니다"를 먼저 말하는 지원자가 훨씬 인상적입니다. 위의 한계들을 면접에서 먼저 꺼낼 수 있으면 실무 감각이 있다는 인상을 줍니다.
