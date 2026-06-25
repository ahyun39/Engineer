# 채용 공고 ETL 파이프라인 — 기술 개념 정리

이 문서는 프로젝트에 사용한 기술들의 개념과 실제 적용 방식을 단계별로 정리합니다.

---

## 목차

1. [ETL 파이프라인이란?](#1-etl-파이프라인이란)
2. [Extract — 웹 크롤링](#2-extract--웹-크롤링)
3. [Kafka — 메시지 큐](#3-kafka--메시지-큐)
4. [Transform — 데이터 정제](#4-transform--데이터-정제)
5. [Elasticsearch — 저장 & 검색](#5-elasticsearch--저장--검색)
6. [Kibana — 시각화](#6-kibana--시각화)
7. [Docker & Docker Compose — 인프라](#7-docker--docker-compose--인프라)
8. [crontab — 스케줄링](#8-crontab--스케줄링)

---

## 1. ETL 파이프라인이란?

### 개념

ETL은 **E**xtract → **T**ransform → **L**oad의 약자로, 외부 소스에서 데이터를 가져와 분석 가능한 형태로 바꾼 뒤 저장소에 적재하는 데이터 처리 흐름이다.

```
[외부 소스]  →  Extract  →  Transform  →  Load  →  [분석/시각화]
사람인 웹      크롤링        정제·구조화     ES 적재     Kibana Dashboard
```

| 단계 | 하는 일 | 이 프로젝트 |
|------|---------|------------|
| Extract | 원천 데이터를 있는 그대로 수집 | 사람인 HTML → DataFrame → raw JSONL |
| Transform | 분석 가능한 형태로 정제·변환 | 날짜 파싱, 텍스트 정제, 구조화 → processed JSONL |
| Load | 최종 저장소에 적재 | Elasticsearch bulk upsert |

### 배치 vs 실시간

| 방식 | 설명 | 이 프로젝트 |
|------|------|------------|
| 배치(Batch) | 일정 주기로 쌓인 데이터를 한꺼번에 처리 | 11:00, 18:00 하루 2회 |
| 스트리밍(Streaming) | 데이터가 발생하는 즉시 처리 | 미사용 (Kafka는 배치 버퍼로 활용) |

채용 공고는 실시간성이 크게 중요하지 않아 배치 방식을 선택했다.  
단, Kafka를 중간에 두어 수집·처리 프로세스를 분리함으로써 장애 격리와 확장성을 확보했다.

### 원본 컬럼을 유지하는 이유

Transform 단계에서 `deadline` → `deadline_date`, `career` → `career_level + employment_type`처럼 파생 컬럼을 만들 때 **원본 컬럼을 삭제하지 않는다.**  
이유는 두 가지다.

1. **디버깅**: 파싱 로직에 버그가 있어도 원본 텍스트가 있으면 재처리가 가능하다.
2. **감사(Audit)**: "이 데이터가 어디서 왔는가"를 언제든 추적할 수 있다.

다만 Elasticsearch 색인 시에는 운영에 불필요한 원본 컬럼(`career`, `registered_at`, `error_msg`)을 `LOAD_COLUMNS` 목록에서 제외해 저장 공간을 절약한다.

---

## 2. Extract — 웹 크롤링

### 웹 크롤링 원리

브라우저가 웹페이지를 여는 과정을 코드로 재현하는 것이다.

```
[브라우저/코드]  →  HTTP GET 요청  →  [웹 서버]
                ←  HTML 응답      ←
HTML 파싱 → 원하는 데이터 추출
```

- **requests**: Python HTTP 클라이언트 라이브러리. `requests.get(url)` 한 줄로 HTML을 가져온다.
- **BeautifulSoup**: HTML 문자열을 파싱해 CSS 선택자로 원하는 태그를 찾아주는 라이브러리.

### 사람인의 HTML 구조

사람인 채용 목록 페이지는 공고 하나를 `div.list_item`으로 감싼다.  
그 안에 회사명, 공고명, 직무 태그, 근무 조건이 각자 다른 CSS 클래스로 분리돼 있다.

```
div.list_item              ← 공고 하나
├── div.company_nm
│   └── a.str_tit          ← 회사명
├── div.job_tit
│   └── a.str_tit          ← 공고명 + href (rec_idx 포함)
├── div.job_meta
│   └── span.job_sector
│       └── span × N       ← 직무 태그 (배열)
└── div.col.recruit_info
    ├── p.work_place        ← 근무지
    ├── p.career            ← 경력·고용형태
    ├── p.education         ← 학력
    ├── p.salary            ← 급여
    ├── span.date           ← 마감일
    └── span.deadlines      ← 등록일
```

### scraper.py 구현 상세

#### URL 설계

```python
BASE_URL = "https://www.saramin.co.kr"
LIST_URL = f"{BASE_URL}/zf_user/jobs/public/list/"
# page 파라미터로 페이지 번호 지정, isAjaxRequest=y로 JSON이 아닌 HTML 응답 요청
response = requests.get(LIST_URL, params={"page": page, "isAjaxRequest": "y"}, headers=HEADERS)
```

`isAjaxRequest=y`를 붙이면 전체 페이지 HTML이 아닌 목록 부분만 응답한다. 이렇게 하면 불필요한 헤더/푸터 HTML을 파싱하지 않아도 된다.

#### User-Agent 설정

```python
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 ..."
    )
}
```

웹 서버는 `User-Agent` 헤더로 요청자가 브라우저인지 봇인지 구분한다. 브라우저처럼 위장하지 않으면 요청이 차단될 수 있다.

#### job_id 추출

```python
href = title_tag["href"]
# href 예시: /zf_user/jobs/relay/view?view_type=public-recruit&rec_idx=54204286
rec_idx = re.search(r"rec_idx=(\d+)", href).group(1)
# 결과: "54204286"
```

`rec_idx`는 사람인이 각 공고에 부여하는 고유 ID다. URL에서 정규식으로 추출해 `job_id`로 사용한다.  
이 값이 나중에 Elasticsearch의 `_id`로 쓰여 **재수집 시 중복을 막는 핵심 키**가 된다.

#### 에러 처리 전략

공고 하나가 파싱에 실패해도 전체 수집이 중단되지 않도록 `try-except`로 감싼다.  
실패한 공고는 `status: "error"`와 에러 메시지를 담은 fallback 레코드로 저장해 **오류 추적이 가능**하게 한다.

```python
for item in jobs:
    try:
        results.append(parse_job(item))
    except Exception as e:
        results.append(build_error_record(item, e))  # 실패해도 계속 진행
```

`build_error_record()`는 `fallback_job_id()`를 통해 HTML 태그의 `id` 속성(`rec-54204286`)에서라도 job_id를 복구하려 시도한다.

#### 원시 데이터 저장 — JSONL

```python
df.to_json(path, orient="records", lines=True, force_ascii=False)
# 저장 결과 예시 (한 줄 = 공고 하나):
# {"job_id":"54204286","company_nm":"(주)카카오","job_tit":"IT 정책...","job_meta":["사무직",...],...}
# {"job_id":"54204194","company_nm":"(주)카카오","job_tit":"선물하기...","job_meta":["이커머스",...],...}
```

**JSONL(JSON Lines)**: 한 줄에 JSON 객체 하나씩 저장하는 형식이다.  
일반 JSON 배열(`[{...}, {...}]`)과 달리 파일을 전부 읽지 않고 **한 줄씩 스트리밍 처리**할 수 있어 대용량 데이터에 적합하다.

---

## 3. Kafka — 메시지 큐

### 메시지 큐란?

생산자(Producer)와 소비자(Consumer) 사이에 데이터를 임시로 보관하는 **중간 저장소**다.  
생산자는 데이터를 큐에 넣고 즉시 다음 작업으로 넘어가고, 소비자는 자신의 속도로 꺼내간다.

```
Kafka 없이:
  크롤러 → 직접 ETL → ES  (ES가 다운되면 크롤러도 멈춤)

Kafka 있을 때:
  크롤러 → Kafka → ETL → ES
            ↑
            메시지 영속 보관 (ES가 다운돼도 나중에 처리 가능)
```

### 핵심 용어

| 용어 | 설명 |
|------|------|
| **Broker** | Kafka 서버. 메시지를 저장하고 전달하는 주체 |
| **Topic** | 메시지를 분류하는 채널 이름. 이 프로젝트: `saramin-jobs-raw` |
| **Partition** | Topic을 물리적으로 나눈 단위. 병렬 처리를 위해 여러 개로 나눌 수 있음 (이 프로젝트: 1개) |
| **Offset** | 파티션 내 메시지의 순서 번호 (0, 1, 2, ...). Consumer가 어디까지 읽었는지 추적 |
| **Producer** | Topic에 메시지를 발행하는 클라이언트. → `kafka_producer.py` |
| **Consumer** | Topic에서 메시지를 구독하는 클라이언트. → `etl_worker.py` |
| **Consumer Group** | 같은 Topic을 나눠 읽는 Consumer들의 묶음. Group 내에서 한 Partition은 한 Consumer만 읽음 |

#### Offset과 재처리

```
Partition: saramin-jobs-raw
offset:  0    1    2    3   ... 195
       [msg][msg][msg][msg] ... [msg]

Consumer Group "etl-worker":
  현재 읽은 위치(committed offset) = 100
  → 재시작 시 offset 100부터 이어서 처리
```

`auto_offset_reset="earliest"`: Consumer Group이 처음 시작될 때 가장 오래된 메시지(offset 0)부터 읽는다.  
`enable_auto_commit=True`: 처리한 offset을 Kafka에 자동으로 기록해 재시작 시 중복 처리를 줄인다.

### KRaft 모드

전통적인 Kafka는 메타데이터 관리를 위해 **ZooKeeper**라는 별도 서비스가 필요했다.  
Kafka 3.3부터 ZooKeeper 없이 Kafka 자체가 메타데이터를 관리하는 **KRaft(Kafka Raft)** 모드가 정식 지원된다.

```
기존 방식:
  ZooKeeper (3개 이상) + Kafka Broker → 설치·운영 복잡

KRaft 방식 (이 프로젝트):
  Kafka Broker + Controller (같은 프로세스) → 단순, 경량
```

`docker-compose.yml`에서 KRaft 관련 환경변수:

```yaml
KAFKA_PROCESS_ROLES: broker,controller   # 하나의 프로세스가 두 역할 담당
KAFKA_NODE_ID: 1                         # 이 노드의 ID
KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093  # Raft 투표 참여자 목록
KAFKA_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
# 9092: 클라이언트(Producer/Consumer) 연결
# 9093: 내부 Raft 통신
```

### kafka_producer.py 구현 상세

```python
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False, default=str).encode("utf-8"),
    acks="all",    # 모든 replica가 저장했다는 확인을 받아야 전송 완료 처리
    retries=3,     # 실패 시 최대 3회 재시도
)
```

- **`bootstrap_servers`**: 처음 연결할 Kafka 브로커 주소. 여러 브로커가 있으면 쉼표로 나열. Kafka는 이 주소로 전체 클러스터 정보를 받아온다.
- **`value_serializer`**: 메시지를 bytes로 변환하는 함수. Python dict → JSON 문자열 → UTF-8 bytes.
- **`default=str`**: `datetime` 등 JSON 기본 직렬화가 안 되는 타입을 문자열로 변환.
- **`acks="all"`**: 브로커가 메시지를 디스크에 썼다는 확인(ACK)을 받고 나서 다음 메시지로 넘어감. 데이터 유실 방지.

```python
for record in df.to_dict(orient="records"):
    producer.send(TOPIC, value=record)  # 비동기 발행 (버퍼에 쌓임)
producer.flush()   # 버퍼에 쌓인 메시지를 브로커에 모두 전송 완료될 때까지 대기
producer.close()   # 연결 종료
```

`send()`는 즉시 전송하지 않고 내부 버퍼에 쌓는다. `flush()`를 호출해야 버퍼를 비우고 전송이 보장된다.

### etl_worker.py 구현 상세

#### poll() 메커니즘

```python
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers="localhost:9092",
    group_id="etl-worker",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=_deserialize,  # bytes → dict (또는 None)
)

poll_result = consumer.poll(timeout_ms=5_000)
# poll_result: {TopicPartition → [ConsumerRecord, ...]}
# timeout_ms: 5초 동안 메시지를 기다림. 없으면 빈 dict 반환
```

`poll()`은 Kafka 브로커에서 여러 메시지를 한 번에 가져온다. 5초마다 호출해 새 메시지를 확인한다.

#### 비JSON 메시지 처리 — _deserialize()

```python
def _deserialize(v):
    if not v:
        return None
    try:
        return json.loads(v.decode("utf-8"))
    except Exception:
        return None  # 파싱 실패 시 None 반환
```

개발 중 브로커 연결 확인용으로 `b'ping'` 같은 테스트 메시지를 보낼 수 있다.  
이런 비JSON 메시지가 `earliest` 오프셋에 남아있으면, Consumer가 재시작할 때 읽어 `JSONDecodeError`가 발생한다.  
`_deserialize()`에서 예외를 잡아 `None`을 반환하고, Worker 루프에서 `None`을 건너뜀으로써 해결했다.

#### 배치 Flush 로직

```python
FLUSH_SECONDS = 30   # 마지막 메시지 수신 후 30초 경과 시 배치 처리

batch = []
last_received_at = None

while True:
    poll_result = consumer.poll(timeout_ms=5_000)

    if poll_result:
        for messages in poll_result.values():
            for msg in messages:
                if msg.value is None:      # 비JSON 메시지 건너뜀
                    continue
                batch.append(msg.value)
        last_received_at = datetime.now()

    # 배치에 메시지가 있고, 30초 이상 새 메시지가 없으면 처리
    if batch and last_received_at:
        idle_sec = (datetime.now() - last_received_at).seconds
        if idle_sec >= FLUSH_SECONDS:
            process_batch(batch)   # transform → save_processed → load
            batch = []
            last_received_at = None
```

**왜 이 방식인가?**  
Producer가 200건을 발행하면 Consumer는 이를 여러 번의 `poll()` 호출로 나눠 받는다.  
"마지막 메시지 이후 30초"를 트리거로 삼으면 모든 메시지가 도착한 뒤 한 번만 배치 처리할 수 있다.

#### 종료 시 잔여 배치 처리

```python
except KeyboardInterrupt:
    pass
finally:
    if batch:
        process_batch(batch)   # Ctrl+C 눌러도 남은 메시지 처리 후 종료
    consumer.close()
```

---

## 4. Transform — 데이터 정제

### 왜 Transform이 필요한가?

사람인에서 수집한 원시 데이터는 사람이 읽기 위한 텍스트 형식이다.  
이걸 그대로 Elasticsearch에 넣으면 집계·필터·시계열 분석이 불가능하다.

| 컬럼 | 원시 값 | 문제 | 변환 결과 |
|------|---------|------|----------|
| `deadline` | `"~06.30(화)"` | 날짜가 아닌 텍스트 | `deadline_date: 2026-06-30` |
| `registered_at` | `"27분 전 등록"` | 상대적 시간 | `registered_at_dt: 2026-06-17 13:33:00` |
| `career` | `"신입 · 경력 · 정규직"` | 두 정보가 혼합 | `career_level: ["신입","경력"]`, `employment_type: ["정규직"]` |
| `company_nm` | `"(주)카카오"` | 법인 표기 혼재 | `company_nm: "카카오"` |
| `work_place` | `"경기 성남시 분당구 외"` | 시·도·구 미분리 | `city: "경기"`, `district: "성남시 분당구"` |
| `salary` | `"3,500만원"` | 숫자가 아닌 텍스트 | `salary_amount: 35000000` |

### deadline_date 파싱

마감일 표기 패턴은 4가지다.

```python
def parse_deadline(deadline_text, reference_dt):
    text = deadline_text.strip()

    # 패턴 1: "내일마감"
    if "내일마감" in text:
        return (reference_dt + timedelta(days=1)).date()

    # 패턴 2: "오늘마감" 또는 "HH시 마감"
    if "오늘마감" in text or re.search(r"\d{1,2}시\s*마감", text):
        return reference_dt.date()

    # 패턴 3: "D-N" (N일 후)
    m = re.match(r"D-(\d+)", text)
    if m:
        return (reference_dt + timedelta(days=int(m.group(1)))).date()

    # 패턴 4: "~MM.DD(요일)" → 연도 추론 필요
    m = re.search(r"(\d{1,2})\.(\d{1,2})", text)
    if m:
        month, day = int(m.group(1)), int(m.group(2))
        deadline_date = datetime(reference_dt.year, month, day).date()

        # 핵심: 계산된 날짜가 수집 시점보다 과거면 다음 해로 보정
        # 예) 12월에 "~01.15" 공고 수집 → 내년 1월 15일
        if deadline_date < reference_dt.date():
            deadline_date = datetime(reference_dt.year + 1, month, day).date()

        return deadline_date

    return None  # "상시채용" 등 패턴 미해당 → 결측 처리
```

### registered_at_dt 파싱

```python
def parse_registered_at(registered_text, reference_dt):
    text = registered_text.strip()
    # "27분 전 등록" → crawl_time - 27분
    m = re.match(r"(\d+)분 전", text)
    if m:
        return reference_dt - timedelta(minutes=int(m.group(1)))
    # "2시간 전 등록" → crawl_time - 2시간
    m = re.match(r"(\d+)시간 전", text)
    if m:
        return reference_dt - timedelta(hours=int(m.group(1)))
    # "3일 전 등록" → crawl_time - 3일
    m = re.match(r"(\d+)일 전", text)
    if m:
        return reference_dt - timedelta(days=int(m.group(1)))
    return None
```

`crawl_time`을 기준으로 역산한다. 이렇게 해야 매번 다른 수집 시점을 기준으로 정확한 절대 시각을 구할 수 있다.

### career 분리

```python
CAREER_LEVELS = {"신입", "경력", "경력무관"}

def split_career(text):
    # "신입 · 경력 · 정규직 외" → ["신입", "경력", "정규직 외"]
    tokens = text.split(" · ")
    levels = [t for t in tokens if t in CAREER_LEVELS]        # ["신입", "경력"]
    types  = [t for t in tokens if t not in CAREER_LEVELS]    # ["정규직 외"]
    return levels or None, types or None
```

`CAREER_LEVELS`에 속하면 경력 수준, 아니면 고용형태로 분류한다.  
결과가 리스트인 이유는 "신입 · 경력"처럼 복수 조건인 공고가 존재하기 때문이다.

### company_nm 정제

```python
def clean_company_nm(text):
    text = re.sub(r"\([^)]*\)", "", text)  # (주), (유), (재) 등 괄호 표기 제거
    text = text.replace("㈜", "")           # 특수문자 ㈜ 제거
    return text.strip()
# "(주)카카오" → "카카오"
# "트루넥스(주)" → "트루넥스"
# "에스케이하이닉스(주)" → "에스케이하이닉스"
```

### work_place 분리

```python
def split_work_place(text):
    # 특수 케이스: "서울전체" (공백 없이 "전체" 포함)
    if "전체" in text and " " not in text:
        return text.replace("전체", ""), "전체"

    # 일반 케이스: 첫 번째 공백 기준으로 분리
    tokens = text.split(" ", 1)   # maxsplit=1: 첫 공백에서만 분리
    city     = tokens[0]          # "경기"
    district = tokens[1] if len(tokens) > 1 else None  # "성남시 분당구"
    return city, district
# "경기 성남시 분당구" → city="경기", district="성남시 분당구"
# "서울 중구"         → city="서울", district="중구"
# "세종 세종특별자치시" → city="세종", district="세종특별자치시"
```

`district` 결측 2건은 "세종 세종특별자치시" 같이 시·도·구 구분이 모호한 특수 행정구역이다.

### 데이터 품질 점검

```python
def log_data_quality(df):
    # 1. 컬럼별 결측치 개수
    print(df.isna().sum())

    # 2. salary_amount 이상치: 0인데 "협의"가 아닌 경우
    anomaly = df[(df["salary_amount"] == 0) & (~df["salary"].str.contains("협의|채용시", na=False))]
    print("salary_amount=0 인데 협의류 표현이 아닌 행:", len(anomaly))

    # 3. 분리 실패 건수
    print("career_level 분리 실패:", df["career_level"].isna().sum())
    print("employment_type 분리 실패:", df["employment_type"].isna().sum())
    print("district 분리 실패:", df["district"].isna().sum())
```

**실제 실행 결과**: district 2건 외 모든 컬럼 결측 0건, 이상치 0건 확인.

---

## 5. Elasticsearch — 저장 & 검색

### Elasticsearch란?

**역색인(Inverted Index)** 기반의 분산 검색 엔진이다.  
관계형 DB가 "어떤 행에 이 값이 있는가"를 저장한다면, ES는 "이 단어가 어떤 문서에 있는가"를 미리 만들어둔다.

```
일반 DB (행 기반):
  doc1: {job_tit: "데이터 엔지니어 채용"}
  doc2: {job_tit: "AI 엔지니어 모집"}

역색인 (단어 기반):
  "데이터"  → [doc1]
  "엔지니어" → [doc1, doc2]
  "채용"    → [doc1]
  "AI"      → [doc2]
  "모집"    → [doc2]
```

검색어 "엔지니어"를 찾으면 역색인에서 즉시 `[doc1, doc2]`를 반환한다. 전체 문서를 스캔하지 않아 속도가 빠르다.

### RDB vs Elasticsearch 비교

| 개념 | RDB | Elasticsearch |
|------|-----|---------------|
| 저장 단위 | Row | Document (JSON) |
| 테이블 | Table | Index |
| 컬럼 정의 | Schema | Mapping |
| 기본 키 | Primary Key | `_id` |
| 쿼리 언어 | SQL | DSL (JSON 형식) / KQL |

### Mapping & Field Types

Mapping은 각 필드의 데이터 타입을 미리 선언하는 **스키마 정의**다.  
Mapping을 선언하지 않으면 ES가 첫 문서 기준으로 자동 추론하는데, 날짜가 문자열로 인식되는 등 의도와 다르게 잡힐 수 있다.

```python
MAPPING = {
    "mappings": {
        "properties": {
            # text: 전문 검색 가능 (역색인 생성, 형태소 분석 적용)
            # keyword: 정확한 값 일치 검색 + 집계(aggregation) 가능
            "company_nm": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}}
                # → company_nm: 전문 검색 / company_nm.keyword: 집계
            },
            "job_tit": {"type": "text"},

            # keyword 배열: 각 요소가 독립적으로 역색인 → terms 집계 가능
            "job_meta":        {"type": "keyword"},
            "career_level":    {"type": "keyword"},
            "employment_type": {"type": "keyword"},

            # date: 날짜 범위 필터, date histogram 가능
            "deadline_date":    {"type": "date"},
            "registered_at_dt": {"type": "date"},
            "crawl_time":       {"type": "date"},

            "salary_amount": {"type": "integer"},
            "is_closed":     {"type": "boolean"},
        }
    }
}
```

#### keyword vs text

| 타입 | 역할 | 주요 사용처 |
|------|------|------------|
| `keyword` | 정확한 값 저장. 집계·정렬·필터에 사용 | `city`, `career_level`, `employment_type` |
| `text` | 텍스트를 형태소로 쪼개 역색인. 전문 검색에 사용 | `job_tit`, `company_nm` |

`city`를 `text`로 저장하면 "서울"을 검색할 때 "서울특별시"도 매칭될 수 있어 집계 결과가 부정확해진다.  
`keyword`로 저장하면 "서울" = "서울"로만 집계한다.

### job_id를 _id로 사용하는 이유

```python
yield {
    "_index": INDEX_NAME,
    "_id": job_id,       # ← ES 문서의 기본 키
    "_source": doc,
}
```

같은 `_id`로 문서를 다시 색인하면 ES는 **덮어쓰기(upsert)** 한다.  
하루 2번 크롤링해도 같은 공고가 중복으로 쌓이지 않고, 마감일·등록일 정보가 최신 값으로 갱신된다.

### bulk API

```python
from elasticsearch.helpers import bulk

success, errors = bulk(es, _to_actions(df), raise_on_error=False)
```

ES REST API는 문서 하나마다 HTTP 요청을 보낼 수 있다.  
200건이면 200번의 HTTP 왕복이 필요하다. `bulk()` API는 여러 문서를 **하나의 HTTP 요청**으로 묶어 보내 성능을 크게 향상한다.

```
일반 방식:
  POST /saramin-jobs/_doc/54204286 → 응답
  POST /saramin-jobs/_doc/54204194 → 응답
  ... × 200

bulk 방식:
  POST /_bulk
  { "index": { "_index": "saramin-jobs", "_id": "54204286" } }
  { "company_nm": "카카오", ... }
  { "index": { "_index": "saramin-jobs", "_id": "54204194" } }
  { "company_nm": "카카오", ... }
  ... (200건을 한 번에)
  → 응답 1번
```

### 배열 필드와 terms aggregation

```python
# 문서에 저장된 값
{"job_meta": ["데이터엔지니어", "정보보안", "AI(인공지능)"]}

# ES 역색인 결과 (자동으로 각 요소를 분리)
"데이터엔지니어" → [doc1, doc7, doc42, ...]
"정보보안"       → [doc1, doc15, ...]
"AI(인공지능)"   → [doc1, doc3, ...]
```

ES는 배열 필드를 저장할 때 각 요소를 **독립적으로 역색인**한다.  
Kibana에서 `job_meta` terms aggregation을 실행하면 `["데이터엔지니어", "정보보안"]`이 하나의 버킷으로 묶이는 것이 아니라, "데이터엔지니어" 버킷에 1 추가, "정보보안" 버킷에 1 추가로 각각 카운팅된다.

### _clean() 함수

```python
def _clean(v):
    if isinstance(v, list):
        return v if v else None      # 빈 리스트 → None (ES에 색인 안 함)
    if v is None:
        return None
    try:
        if isinstance(v, float) and math.isnan(v):
            return None              # NaN → None (pandas NaN을 ES가 처리 못함)
    except (TypeError, ValueError):
        pass
    return v
```

pandas DataFrame에서 결측치는 `float('nan')`으로 표현된다. JSON 직렬화 시 `NaN`은 유효하지 않은 값이므로 ES가 거부한다. `_clean()`에서 `None`으로 변환하고, `None` 필드는 `_source`에서 제거해 색인하지 않는다.

---

## 6. Kibana — 시각화

### Data View

Kibana가 어떤 ES 인덱스를 읽을지, 어떤 필드를 타임스탬프로 쓸지 지정하는 설정이다.

```
Stack Management → Data Views → Create data view
  Index pattern: saramin-jobs      ← 대상 인덱스
  Timestamp field: crawl_time      ← 시계열 기준 필드
```

`crawl_time`을 타임스탬프로 지정하면 Kibana의 시간 범위 필터가 `crawl_time` 기준으로 작동한다.

### Discover

Data View로 색인된 문서를 테이블 형태로 탐색하는 화면이다.  
KQL(Kibana Query Language)로 필터를 걸 수 있다.

```
예: career_level:"신입" AND city:"서울"
    → 서울의 신입 공고만 필터링
```

### Lens & Dashboard 패널 구성

이 프로젝트에서 구성한 6개 분석 패널:

| 패널 | 차트 타입 | X/Y 축 또는 집계 기준 | 인사이트 |
|------|-----------|----------------------|---------|
| 경력별 공고 수 | Stacked Bar | X: `career_level`, Color: `city` | 신입/경력별 지역 분포 |
| 지역별 공고 수 | Horizontal Bar | Y: `city`, X: Count | 채용 밀집 지역 |
| 경력별 고용형태 | Stacked Bar | X: `career_level`, Color: `employment_type` | 신입 정규직 비율 |
| 인기 직무 태그 | Horizontal Bar | Y: `job_meta`, X: Count | 수요 높은 직무 태그 |
| 학력 조건별 고용형태 | Stacked Bar | X: `education`, Color: `employment_type` | 학력별 채용 형태 |
| 마감일별 공고 수 | Bar | X: `deadline_date` per week, Y: Count | 마감 임박 공고 현황 |

---

## 7. Docker & Docker Compose — 인프라

### 컨테이너란?

애플리케이션과 그 실행 환경(라이브러리, 설정)을 **하나의 격리된 패키지**로 묶은 것이다.  
"내 PC에서는 되는데 서버에서는 안 된다"는 문제를 해결한다.

```
컨테이너 없이:
  개발자 A PC: Java 11, Elasticsearch 7.x 설치
  개발자 B PC: Java 17, Elasticsearch 8.x 설치 → 버전 충돌

컨테이너 사용:
  docker pull elasticsearch:8.13.0  → 누구나 동일한 환경
```

### docker-compose.yml 구조

`docker-compose.yml` 하나로 Kafka, Elasticsearch, Kibana 세 서비스를 함께 정의하고 관리한다.

```yaml
services:
  kafka:
    image: apache/kafka:3.7.0       # 사용할 Docker 이미지
    container_name: recruit-kafka   # 컨테이너 이름 (다른 서비스에서 참조 시 사용)
    ports:
      - "9092:9092"   # 호스트포트:컨테이너포트 (외부에서 localhost:9092로 접근)
    environment:
      # KRaft 모드 설정값 (환경변수로 Kafka 설정 주입)
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      ...
    volumes:
      - kafka_data:/var/lib/kafka/data  # 데이터 영속화 (컨테이너 삭제 후에도 데이터 유지)
    healthcheck:
      test: ["CMD", "/opt/kafka/bin/kafka-topics.sh", "--bootstrap-server", "localhost:9092", "--list"]
      interval: 10s   # 10초마다 확인
      timeout: 5s     # 5초 이내 응답 없으면 실패
      retries: 10     # 10번 실패 시 unhealthy 상태

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.13.0
    environment:
      - discovery.type=single-node        # 단일 노드 모드 (클러스터 불필요)
      - xpack.security.enabled=false      # 로컬 개발 시 인증 비활성화
      - ES_JAVA_OPTS=-Xms512m -Xmx512m   # JVM 힙 메모리 제한 (512MB)
    ...

  kibana:
    image: docker.elastic.co/kibana/kibana:8.13.0
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      #                              ↑
      #  컨테이너명으로 ES에 접근 (Docker 내부 DNS가 IP로 변환)
    depends_on:
      elasticsearch:
        condition: service_healthy  # ES healthcheck 통과 후에만 Kibana 시작

volumes:
  kafka_data:   # Docker managed volume (호스트 경로 자동 지정)
  es_data:
```

#### healthcheck가 필요한 이유

`depends_on`만 쓰면 "컨테이너가 시작됐는가"만 확인한다. Kafka나 ES는 컨테이너가 시작된 뒤에도 내부 초기화에 수초~수십 초가 걸린다.  
`condition: service_healthy`를 쓰면 **실제로 서비스가 준비됐을 때**까지 기다린다.

#### Volume과 데이터 영속화

```
컨테이너는 삭제하면 내부 데이터도 사라진다.
Volume을 마운트하면 컨테이너 외부(Docker 관리 영역)에 데이터가 저장된다.
→ docker compose down 후 다시 up해도 Kafka 메시지와 ES 인덱스가 유지된다.
```

---

## 8. crontab — 스케줄링

### crontab이란?

Unix/macOS 시스템에 내장된 작업 스케줄러다. 특정 시각에 명령어를 자동 실행한다.

### crontab 문법

```
┌─ 분 (0-59)
│  ┌─ 시 (0-23)
│  │  ┌─ 일 (1-31)
│  │  │  ┌─ 월 (1-12)
│  │  │  │  ┌─ 요일 (0-7, 0과 7이 일요일)
│  │  │  │  │
*  *  *  *  *  실행할 명령어
```

#### 이 프로젝트 설정

```crontab
0 11 * * * cd /Users/kangahhyun/Engineer/Projects/project_recruit_etl && \
            /opt/anaconda3/bin/python3 kafka_producer.py >> logs/cron.log 2>&1

0 18 * * * cd /Users/kangahhyun/Engineer/Projects/project_recruit_etl && \
            /opt/anaconda3/bin/python3 kafka_producer.py >> logs/cron.log 2>&1
```

- `0 11 * * *`: 매일 11시 0분에 실행
- `0 18 * * *`: 매일 18시 0분에 실행
- `/opt/anaconda3/bin/python3`: cron은 PATH가 제한적이라 Python 전체 경로를 사용
- `>> logs/cron.log`: 표준 출력을 로그 파일에 추가 저장 (`>>`는 덮어쓰기가 아닌 추가)
- `2>&1`: 표준 에러(2)를 표준 출력(1)으로 합쳐 같은 로그 파일에 기록

#### 왜 `.venv` Python이 아닌 conda Python인가?

`kafka-python-ng` 라이브러리를 conda base 환경에 설치했기 때문이다.  
cron은 별도 셸 환경에서 실행되므로 가상환경을 `source activate`하지 않으면 패키지를 찾지 못한다.  
conda base Python의 전체 경로를 사용하면 이 문제를 우회할 수 있다.

---

## 전체 흐름 한눈에 보기

```
[crontab 11:00 / 18:00]
        │
        ▼
kafka_producer.py
  1. scrape()            ← scraper.py: 사람인 10페이지 크롤링
  2. save_raw(df)        ← data/raw/jobs_raw_YYYYMMDD_HHMMSS.jsonl 저장
  3. KafkaProducer       ← 각 공고를 JSON으로 직렬화
  4. producer.send()     ← saramin-jobs-raw 토픽에 196건 발행
  5. producer.flush()    ← 버퍼 비우기 (전송 보장)
        │
        ▼ (Kafka 토픽에 메시지 보관)
        │
etl_worker.py (상시 실행)
  6. consumer.poll()     ← 5초마다 메시지 확인
  7. batch 누적          ← 30초 idle 시 flush 트리거
  8. transform(df)       ← transformer.py: 정제·파생 컬럼 생성
  9. log_data_quality()  ← 결측치·이상치 리포팅
 10. save_processed(df)  ← data/processed/jobs_processed_YYYYMMDD.jsonl 저장
 11. load(df)            ← loader.py: ES bulk upsert
        │
        ▼
Elasticsearch: saramin-jobs 인덱스
  - job_id = _id → 재수집 시 upsert
  - 196건 색인 완료
        │
        ▼
Kibana: http://localhost:5601
  - Data View: saramin-jobs (crawl_time 기준)
  - Discover: 문서 탐색
  - Dashboard: 6개 분석 패널
```
---

## 9. 포트폴리오 총평 — 카카오뱅크 정보보호 데이터 엔지니어 관점

> 10년차 데이터 엔지니어 + 해당 직무 실무자 관점에서 작성한 리뷰.

### 총평

신입 포트폴리오로서 수준이 높다. Elastic Stack + Kafka 조합을 선택한 것 자체가 이 공고의 우대사항과 정확히 맞아떨어지고, 전체 파이프라인을 처음부터 구현했다는 점도 좋다. 단, 실무자 눈에 바로 보이는 허점들이 있고, 이걸 모르고 제출하면 면접에서 치명적이다.

---

### 잘 한 것 (강점)

**1. 기술 선택이 공고와 정확히 매칭**  
필수 요건인 ETL + Elastic Stack, 우대사항인 Kafka를 직접 골라서 썼다. 단순히 쓴 게 아니라 "왜 썼는가"를 설명할 수 있는 구조다. 이 판단력 자체가 신입에게는 드물다.

**2. 전체 파이프라인을 한 명이 처음부터 구현**  
Extract → Transform → Load를 단계별 모듈로 분리하고, Kafka로 비동기 처리까지 구성했다. 단편적인 튜토리얼 따라하기가 아니라 설계 판단이 들어간 결과물이다.

**3. 문서화 수준**  
README, portfolio.html, study_notes.md, record.ipynb — 이 정도로 문서를 갖춘 신입 포트폴리오는 거의 없다. 실무에서 "문서 쓸 줄 아는 사람"은 드물다.

**4. 데이터 품질 점검 구현**  
`log_data_quality()` 로직이 있다는 게 좋다. 많은 신입이 데이터가 들어오면 그냥 믿는데, 이 코드는 의심한다.

---

### 보완해야 할 것 (우선순위 순)

#### ❶ 가장 치명적: 보안 도메인과의 연결고리가 없음

이 공고는 **정보보호 데이터 엔지니어**다. 직무 설명에 "보안 로그 수집 파이프라인", "보안 시나리오 개발"이 명시되어 있다.  
지금 포트폴리오의 데이터 소스는 **채용 공고**다. 파이프라인 기술은 좋지만 면접관 입장에서는 "왜 보안 데이터가 아니었나?"라는 질문이 나올 수밖에 없다.

최소한 지원서 혹은 면접에서 "이 파이프라인 구조를 보안 로그에 적용하면 어떻게 된다"를 설명할 수 있어야 한다.

```
현재: 채용 공고 → Kafka → ETL → ES → Kibana 채용 현황 Dashboard
설명할 수 있어야 할 것:
  보안 이벤트 로그 → Kafka → ETL → ES → Kibana SIEM Dashboard
  (방화벽 로그, 접근 로그, 이상 행위 탐지 시나리오 등)
```

#### ❷ `print()` 대신 `logging` 모듈을 써야 함 → ✅ 해결 완료 (log_config.py 도입)

실무에서 `print()`로 운영 로그를 남기는 코드는 없다.  
`logging` 모듈을 쓰면 로그 레벨(DEBUG/INFO/WARNING/ERROR) 제어, 파일 로테이션, 구조화된 출력이 가능하다.  
`%s` 스타일 포맷팅을 사용하면 꺼진 레벨의 메시지는 문자열 생성 자체를 건너뛰어 성능도 좋다.

#### ❸ 설정값이 코드에 하드코딩되어 있음

`KAFKA_BOOTSTRAP = "localhost:9092"`, `ES_HOST = "http://localhost:9200"` 등이 각 파일에 흩어져 있다.  
로컬 개발에서는 괜찮지만 실무에서는 환경(개발/스테이징/운영)마다 주소가 다르다.  
`.env` 파일과 `python-dotenv`로 외부화해야 한다.

```python
# .env
KAFKA_BOOTSTRAP=localhost:9092
ES_HOST=http://localhost:9200
FLUSH_SECONDS=30
```

#### ❹ `enable_auto_commit=True`의 위험성을 이해해야 함

`auto_commit`은 `poll()` 호출 시점에 이전 배치의 offset을 자동 커밋한다.  
즉, 커밋 후 `process_batch()` 실행 중 프로세스가 죽으면 **데이터 유실**이 발생한다.  
실무에서는 `enable_auto_commit=False`로 설정하고, `process_batch()`가 성공한 뒤 `consumer.commit()`을 수동으로 호출한다.  
코드를 바꾸지 않더라도, **이 트레이드오프를 알고 선택했다는 것**을 면접에서 설명할 수 있어야 한다.

#### ❺ Logstash를 모른다는 게 드러남

공고의 필수 요건이 **"Elastic Stack에 대한 이해도"**다. Elastic Stack = **E**lasticsearch + **L**ogstash + **K**ibana다.  
이 프로젝트는 E와 K만 쓴다. Logstash를 직접 쓰지 않더라도, "Logstash 대신 Kafka + 커스텀 Consumer를 선택한 이유"를 설명할 수 있어야 한다.

| | Logstash | 이 프로젝트 (Kafka + Python) |
|---|---|---|
| 장점 | 설정 파일(DSL)만으로 파이프라인 정의, 500+ 플러그인 | 복잡한 변환 로직을 Python으로 자유롭게 구현, 장애 격리 |
| 단점 | 복잡한 비즈니스 로직 구현 어려움, 메모리 사용량 큼 | Logstash built-in 플러그인을 직접 구현해야 함 |

#### ❻ 테스트 코드가 전혀 없음

`parse_deadline()`처럼 엣지 케이스가 많은 함수에 단위 테스트가 없다.  
테스트가 없으면 "이 코드가 실제로 맞다고 어떻게 확신하나요?"라는 질문에 답하기 어렵다. 3~5개만 있어도 신뢰도가 올라간다.

```python
# tests/test_transformer.py
def test_deadline_year_rollover():
    # 12월에 수집한 "~01.15" 공고는 다음 해로 보정되어야 한다
    ref = datetime(2026, 12, 20)
    result = parse_deadline("~01.15(목)", ref)
    assert result.year == 2027
```

#### ❼ xpack.security.enabled=false 처리

보안 직무에 지원하는 포트폴리오에서 보안 설정을 끈 채로 제출하면 인식이 좋지 않다.  
최소한 "왜 껐고, 실무에서는 어떻게 달라야 하는지"를 README나 문서에 명시해야 한다.

- TLS 인증 활성화
- 사용자/역할 기반 접근 제어 (RBAC)
- API 키 발급

---

### 면접에서 반드시 나올 질문과 답변 준비

| 예상 질문 | 현재 상태 | 준비해야 할 답 |
|-----------|-----------|---------------|
| "Kafka를 왜 쓰셨나요?" | 설명 가능 ✅ | "수집-처리 분리, ES 장애 격리" 설명 가능 |
| "`enable_auto_commit=True`인데 데이터 유실 가능성은?" | 위험 ❌ | 자동/수동 커밋 트레이드오프 설명 필요 |
| "Logstash는 왜 안 썼나요?" | 설명 없음 ❌ | Logstash vs 커스텀 Consumer 비교 설명 필요 |
| "보안 로그에도 이 파이프라인을 쓸 수 있나요?" | 연결 없음 ❌ | 보안 이벤트 로그 적용 시나리오 설명 필요 |
| "운영 중 파이프라인이 죽으면 어떻게 복구하나요?" | 미흡 ⚠️ | Kafka offset 재처리, 데드레터 큐 개념 필요 |
| "ES xpack.security를 왜 껐나요?" | 주석만 있음 ⚠️ | 로컬 개발 / 실무 보안 설정 차이 설명 필요 |

---

### 최종 판단

이 포트폴리오로 서류는 통과할 수 있다. 공고 필수 요건(ETL, Elastic Stack)과 우대사항(Kafka)을 직접 구현했고, 문서화도 잘 되어 있다.  
다만 면접에서 위에 언급한 기술적 허점이 나오면 그게 탈락 이유가 된다.  
특히 ❶(보안 도메인 연결)과 ❹(auto_commit 트레이드오프)는 반드시 답할 수 있어야 한다.

### 해결 현황

| # | 항목 | 상태 |
|---|------|------|
| ❶ | 보안 도메인 연결고리 | ⚠️ 면접 답변 준비 필요 |
| ❷ | `print()` → `logging` 모듈 교체 | ✅ 완료 (`log_config.py` 도입) |
| ❸ | 설정값 환경변수화 | ⬜ 미완료 |
| ❹ | `auto_commit` 트레이드오프 이해 | ⚠️ 면접 답변 준비 필요 |
| ❺ | Logstash 이해 | ⚠️ 면접 답변 준비 필요 |
| ❻ | 테스트 코드 추가 | ⬜ 미완료 |
| ❼ | xpack.security 설명 추가 | ⬜ 미완료 |

---
## 보완할 점 2 logging으로 변환 과정 정리

```python
변경 과정 설명
1. 왜 중앙 설정 모듈(log_config.py)을 따로 만들었나
5개 파일이 각자 logging.basicConfig()를 호출하면 제일 먼저 호출된 것만 적용됩니다. 나중에 호출된 것은 무시됩니다. 중앙 모듈 하나에서 설정하고 나머지는 get_logger(__name__)만 호출하면 이 문제가 없고, 포맷·파일 경로를 한 곳에서만 관리할 수 있습니다.
2. 로그 레벨을 어떻게 배정했나
|레벨|기준|적용 예시|
|DEBUG|반복적인 진행 상황 — 콘솔 노출 불필요|페이지별 크롤링 진행, 메시지 누적 offset|
|INFO|정상 처리 완료 이벤트|파일 저장 완료, Kafka 발행 완료, 배치 처리 완료|
|WARNING|문제지만 파이프라인은 계속 동작|공고 파싱 실패 1건, district 분리 실패|
|ERROR|실제 오류 — 즉시 확인 필요|ES 적재 실패|
3. %s 스타일 vs f-string

## 이렇게 하지 않음 (f-string: 항상 문자열 생성)
logger.debug(f"메시지 누적: {len(batch)}건")

## 이렇게 함 (% 스타일: DEBUG 레벨이 꺼져 있으면 문자열 생성 자체를 건너뜀)
logger.debug("메시지 누적: %d건", len(batch))
debug() 레벨은 운영 환경에서 보통 꺼져 있습니다. %s 스타일을 쓰면 꺼진 레벨의 메시지는 포맷팅 연산 자체를 건너뛰어 성능이 좋습니다.
4. 콘솔과 파일 출력을 다르게 설정한 이유

콘솔 (StreamHandler) — INFO 이상만
  → 운영 중 터미널에서 핵심 이벤트만 보임

파일 (TimedRotatingFileHandler) — DEBUG 이상 전부
  → 문제 발생 시 파일에서 상세 추적 가능
  → 자정마다 새 파일 생성, 7일치 자동 보관
5. etl_worker.py에서 수동 타임스탬프 제거

## 이전: 타임스탬프를 직접 만들어 print에 포함
print(f"[{datetime.now().strftime('%H:%M:%S')}] 배치 처리 시작: {len(records)}건")

## 이후: logging 포맷터가 자동으로 타임스탬프 붙임
logger.info("배치 처리 시작: %d건", len(records))
## 출력: 2026-06-17 23:23:11 [INFO    ] etl_worker - 배치 처리 시작: 200건
중복 작업이 사라지고 전체 파이프라인의 타임스탬프 형식이 통일됩니다.
6. transformer.py의 이상치 레벨 동적 결정

## 건수가 0이면 INFO, 1 이상이면 WARNING으로 자동 분류
(logger.warning if district_null > 0 else logger.info)(
    "district 분리 실패: %d건", district_null
)
이 방식으로 "결측 없음"과 "결측 있음"이 로그 레벨로 구분되어, 나중에 로그 파일에서 WARNING만 필터링하면 문제 있는 실행만 바로 찾을 수 있습니다.
```

---
## ❸ 설정값 환경변수화 — 해결 과정 상세 설명

```python
**1. 문제 진단: 무엇이 왜 문제인가**

기존 코드는 접속 대상이나 동작 파라미터가 소스 코드 안에 직접 기록되어 있었습니다.

# kafka_producer.py, etl_worker.py

KAFKA_BOOTSTRAP = "localhost:9092"

TOPIC           = "saramin-jobs-raw"

# loader.py

ES_HOST    = "http://localhost:9200"

INDEX_NAME = "saramin-jobs"

# scraper.py

BASE_URL = "https://www.saramin.co.kr"

def scrape(pages=range(1, 11)):  # 페이지 수도 고정

이 방식의 문제는 두 가지입니다.

| **상황** | **문제** |
| --- | --- |
| 로컬 → 운영 서버로 배포할 때 | localhost:9092 → 실제 서버 IP로 코드를 직접 수정해야 함 |
| GitHub에 올릴 때 | 접속 정보가 코드에 노출됨 (보안) |

**좋은 설계 원칙**: "코드(logic)는 git으로 공유하고, 설정(config)은 환경마다 따로 관리한다"

**2. 해결 방법 선택: python-dotenv**

Python에서 환경변수를 관리하는 표준 도구입니다.

- **.env 파일**: 실제 값이 적힌 파일. .gitignore에 등록해서 git에 올리지 않음
- **.env.example 파일**: 어떤 키가 필요한지 알려주는 템플릿. git에 올려서 팀원이 참고
- **python-dotenv**: load_dotenv()로 .env의 내용을 환경변수로 읽어옴

# 동작 흐름

.env 파일 ──→ load_dotenv() ──→ os.getenv("키") ──→ 파이썬 변수

**3. 설계 결정: config.py를 중간 계층으로 두기**

각 파일에서 직접 os.getenv()를 호출하는 대신, config.py 한 곳에서 모두 처리합니다.

# 나쁜 방법 (각 파일마다 흩어짐)

kafka_producer.py:  BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")

etl_worker.py:      BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")

# 좋은 방법 (config.py에 집중)

config.py:          KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")

kafka_producer.py:  from config import KAFKA_BOOTSTRAP

etl_worker.py:      from config import KAFKA_BOOTSTRAP

**장점**: 키 이름이나 기본값을 바꿀 때 config.py 한 파일만 수정하면 됩니다.

**4. 생성/수정한 파일 목록**

**새로 만든 파일 (3개)**

| **파일** | **역할** | **git 추적** |
| --- | --- | --- |
| config.py | os.getenv()로 환경변수를 읽어 상수로 제공 | ✅ 추적 |
| .env | 실제 접속 정보 | ❌ .gitignore에 이미 등록되어 있어 추적 안 됨 |
| .env.example | .env 키 목록 템플릿 | ✅ 추적 (내용은 예시값) |

**수정한 파일 (4개)**

| **파일** | **제거한 하드코딩** | **추가한 import** |
| --- | --- | --- |
| scraper.py | BASE_URL, pages=range(1,11) | SARAMIN_BASE_URL, SCRAPE_PAGES |
| kafka_producer.py | KAFKA_BOOTSTRAP, TOPIC | KAFKA_BOOTSTRAP, KAFKA_TOPIC |
| etl_worker.py | KAFKA_BOOTSTRAP, TOPIC, GROUP_ID, FLUSH_SECONDS, POLL_INTERVAL_MS | 동일 5개 |
| loader.py | ES_HOST, INDEX_NAME | ES_HOST, ES_INDEX |

**5. 핵심 코드 설명: config.py**

load_dotenv()  # .env 파일을 읽어 환경변수로 등록

KAFKA_BOOTSTRAP: str = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")

#                                  ↑ 환경변수 키       ↑ 기본값 (fallback)

os.getenv("키", 기본값) 동작 방식:

1. KAFKA_BOOTSTRAP 환경변수가 있으면 → 그 값 사용
2. 없으면 → "localhost:9092" 사용

**.env 없이도 실행된다**는 게 핵심입니다. 개발 환경에서는 .env 없이 바로 실행하고, 운영 환경에서는 .env를 만들어 값을 재정의할 수 있습니다.

**6. scraper.py의 추가 개선: mutable default argument 버그 제거**

# 변경 전 — 모듈 로드 시점에 range(1, 11)이 한 번만 평가됨

def scrape(pages=range(1, 11)):

# 변경 후 — 함수 호출마다 SCRAPE_PAGES를 새로 읽음

def scrape(pages=None):

if pages is None:

pages = range(1, SCRAPE_PAGES + 1)

기본값이 모듈 로드 시 고정되면, 실행 중 SCRAPE_PAGES 값이 바뀌어도 반영되지 않는 문제가 있습니다. None 패턴으로 바꿔 이 문제도 함께 해결했습니다.

**7. 배포 시 사용법**

# 개발 환경 (기본값으로 실행)

python kafka_producer.py

# .env로 운영 설정 적용

cp .env.example .env

# .env 파일에서 값 수정 후

python kafka_producer.py

# 또는 환경변수를 직접 주입 (CI/CD, Docker 등)

ES_HOST=http://prod-es:9200 KAFKA_BOOTSTRAP=prod-kafka:9092 python kafka_producer.py
```