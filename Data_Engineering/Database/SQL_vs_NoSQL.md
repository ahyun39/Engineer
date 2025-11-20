<center><img src="https://github.com/user-attachments/assets/cd273af5-bc3a-496c-9c1a-7d6791aaa7d1" width="500" height="600"/></center>


<br>

## SQL

SQL은 구조화 질의 언어 (Structured Query Language)로 관계형 데이터베이스를 관리하고 조작하기 위해 특별히 설계된 표준 프로그래밍 언어이다. 쿼리, 업데이트, 데이터 구조 관리 등 다양한 작업을 통해 관계형 데이터베이스 관리 시스템 (RDBMS)에 저장된 데이터와 상호 작용하는 데 사용된다.

### SQL DB 특징

- **구조화된 데이터**
    
    명확한 스키마를 가진 구조화된 데이터에 이상적이다.
    
- **ACID**
    
    원자성(Atomicity), 일관성(Consistency), 격리성(Isolation), 지속성(Durability)을 보장하여 신뢰할 수 있는 트랜잭션을 제공한다.
    
- **스키마 기반**
    
    데이터를 구성하기 위해 미리 정의된 스키마가 필요하다.
    
- **SQL 언어**
    
    데이터베이스 쿼리 및 유지 관리에 SQL을 사용한다.
    
- **확장성**
    
    일반적으로 수직적으로 확장된다.

### SQL DB Category

**1. 관계형 데이터베이스 관리 시스템 (RDBMS)**

<center><img src="https://github.com/user-attachments/assets/dd0c26df-ce5e-4333-9ea5-227ab20e195c" width="300" height="200"/></center>


    - 데이터를 정의하고 조작하기 위해 구조화된 쿼리 언어 (SQL)를 사용한다.
    - 데이터를 테이블에 저장하고 스키마를 사용하여 데이터 무결성과 테이블 간의 관계를 강제한다.
    - 예시 : MySQL, PostgreSQL, Oracle Database, Microsoft SQL Server
    - 트랜잭션 애플리케이션, ERP, 고객 관계 관리(CRM), 재무 기록 등..

**2. OLAP (Online Analytical Processing)**

<center><img src="https://github.com/user-attachments/assets/6071eea4-affc-403b-9bad-0e796f2fdfc3" width="300" height="200"/></center>

    - 복잡한 쿼리를 지원하도록 설계되었으며 데이터 분석과 비즈니스 인텔리전스에 사용된다.
    - 대량의 데이터를 처리할 수 있으며 분석 쿼리에 대해 빠른 응답 시간을 제공한다.
    - 예시 : Microsoft SQL Server Analysis Services (SSAS), Oracle OLAP, SAP BW
    - 데이터 마이닝, 비즈니스 보고, 판매 및 마케팅 분석, 재무 예측 등..

이러한 데이터베이스 유형은 각기 다른 목적을 위해 사용되며 데이터의 특성, 쿼리 유형, 성능 요구 사항 등 애플리케이션의 특정 요구 사항에 따라 선택된다.

### SQL DB를 사용해야 하는 경우

- 데이터가 구조화되어 있고 자주 변경되지 않는다.
- 여러 행 트랜잭션과 복잡한 쿼리가 필요하다.
- 데이터 무결성과 일관성이 중요하다.
- 예측 가능하고 고정된 스키마가 있다.

<br>


## NoSQL

NoSQL은 “Not Only SQL”의 약자로, 전통적인 관계형 데이터베이스와 다른 광범위한 데이터베이스 관리 시스템을 의미한다. 
NoSQL 데이터베이스는 비구조화, 반구조화, 구조화된 데이터를 처리할 수 있도록 설계되었으며, SQL 데이터베이스보다 더 큰 유연성과 확장성을 제공한다. 
대량의 데이터와 실시간 웹 애플리케이션을 처리하는 데 유용하다.

### NoSQL DB 특징

- 유연한 스키마
    
    고정된 스키마 없이 비구조화, 반구조화 또는 구조화된 데이터를 처리할 수 있다.
    
- 최종 일관성
    
    즉각적인 일관성보다는 최종 일관성에 중점을 두어 높은 가용성을 제공한다.
    
- 확장성
    
    수평적 확장성(부하를 분산하기 위해 더 많은 서버 추가)을 위해 설계되었다.
    
- 다양한 데이터 모델
    
    문서, 키-값, 컬럼 패밀리, 그래프 등 다양한 데이터 모델을 지원한다.
    
- 성능
    
    특정 사용 사례에 최적화되어 대량의 데이터에 대해 더 빠른 읽기 및 쓰기 작업을 제공한다.

### NoSQL DB Category

**1. 키-값 저장소 (Key-Value Store)**

<center><img src="https://github.com/user-attachments/assets/ae8d82c7-274f-4905-b97e-38c563527b9c" width="300" height="200"/></center>

    - 키-값 저장소는 간단한 키-값 방식을 사용하여 데이터를 저장하는 NoSQL 데이터베이스 유형이다.
    - 각 데이터 항목은 키와 관련 값으로 저장되며, 사전이나 해시 테이블과 유사하다.
    - 키-값 저장소는 단순성과 키를 알고 있을 때 빠른 값 검색을 위해 설계되었다.
    - 예시 : Redis, DynamoDB, Riak
    - 캐싱, 세션 관리, 사용자 프로필, 구성 관리 등..

**2. 문서 저장소 (Document Store)**

<center><img src="https://github.com/user-attachments/assets/688d0188-7b39-4a49-990f-61757946019a" width="300" height="200"/></center>

    - 문서 저장소는 문서 지향 정보를 저장, 검색 및 관리하도록 설계된 또 다른 유형의 NoSQL 데이터베이스이다.
    - 문서는 일반적으로 JSON, BSON 또는 XML 과 같은 형식으로 저장되어 컬렉션 내에서 문서마다 다를 수 있는 유연한 스키마를 허용한다.
    - 예시 : MongoDB, CouchDB, RavenDB
    - 콘텐츠 관리 시스템, 전자 상거래 애플리케이션, 실시간 분석 등..

**3. 그래프 데이터베이스**

<center><img src="https://github.com/user-attachments/assets/13896cd4-2df4-47ef-a967-ef3e95fed70d" width="300" height="200"/></center>

    - 그래프 데이터베이스는 노드, 엣지, 속성을 사용하여 데이터를 표현하고 저장하는 의미론적 쿼리를 위해 그래프 구조를 사용한다.
    - 그래프 데이터베이스는 특히 엔터티 간의 관계를 탐색하는 데 적합하다.
    - 예시 : Neo4j, ArangoDB, Amazon Neptune
    - 소셜 네트워크, 추천 엔지, 사기 감지, 네트워크 및 IT 운영

**4. 칼럼 저장소**

<center><img src="https://github.com/user-attachments/assets/02e163fb-3685-4830-bb57-e9f0187d0a02" width="300" height="200"/></center>

    - 칼럼 저장소(or 칼럼 패밀리 저장소)는 행이 아닌 열별로 데이터를 저장하는 NoSQL 데이터베이스 유형이다.
    - 큰 데이터셋에 대한 집계와 요약이 일반적인 분석적 쿼리 워크로드에 특히 유리하다.
    - 예시 : Apache Cassandra, HBase, Google Bigdata
    - 데이터 웨어하우징, 비즈니스 인텔리전스, 실시간 분석 등..

### NoSQL DB 사용해야 하는 경우

- 대량의 비구조화 또는 반구조화된 데이터를 다루고 있다.
- 일관성보다는 확장성과 성능이 우선순위다.
- 애플리케이션이 변화하는 데이터 요구사항에 적응하기 위해 유연한 스키마가 필요하다.
- 대규모 분산 데이터를 처리하고 있다.

<br>

### SQL vs. NoSQL

|  | SQL | NoSQL |
| --- | --- | --- |
| 데이터 모델 | 테이블, 행, 열이 이 있는 관계형 | 다양한 데이터 모델(문서, 키-값, 컬럼 패밀리, 그래프)이 있는 비관계형 |
| 스키마 | 고정된 스키마; 미리 정의된 테이블과 열 | 동적 스키마; 유연하고 적응 가능 |
| 쿼리 언어 | SQL | 데이터베이스 유형에 따라 다양함; 예 ) MongoDB는 JSON과 유사한 쿼리 사용 |
| 확장성 | 수직적 | 수평적 |
| 일관성 | ACID 준수; 강력한 일관성 보장 | 일반적으로 최종 일관성을 제공하며, 필요한 경우 더 강력한 일관성으로 조정 가능 |
| 사용 사례 | 여러 행 트랜잭션, 복잡한 쿼리, 일관성이 필요한 애플리케이션에 최적 | 대규모 데이터 저장, 실시간 분석, 유연한 데이터 모델이 필요한 애플리케이션에 이상적 |


<br>
<br>

reference - https://maily.so/devpill/posts/4de76bcc