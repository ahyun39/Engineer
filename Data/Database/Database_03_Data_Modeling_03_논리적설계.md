# Relational Modeling

<br>

### 논리적 모델의 개념과 특성

- ER 다이어그램으로 표현된 개념적 구조를 데이터베이스에 저장할 형태로 표현한 논리적 구조
    - 예 ) 데이터베이스의 논리적 구조 = 데이터베이스 스키마(schema)

- 계층 데이터 모델, 네트워크 데이터 모델, 관계 데이터 모델 등이 있음

<br>
<br>

### Hierarchical Data Model

- 데이터베이스의 논리적 구조가 트리 형태임
    - 루트 역할을 하는 개체가 존재하고 사이클이 존재하지 않음
    - 두 개체 사이에 하나의 관계만 정의할 수 있음

- 개체 간에 상하 관계가 성립
    - 부모 개체 / 자식 개체
    - 부모와 자식 개체는 일대다 관계만 허용됨

- 제약 사항
    - 다대다 관계를 직접 표현할 수 없음
    - 개념적 구조를 모델링하기 어려워 구조가 복잡해질 수 있음
    - 데이터의 삽입, 삭제, 수정, 검색이 쉽지 않음

<br>
<br>

### Network Data Model

- 데이터베이스의 논리적 구조가 네트워크, 즉 그래프 형태임
    - 두 개체 사이에 여러 관계를 정의할 수 있어 이름으로 구별함

- 개체 간에는 일대다 관계만 허용됨

- 제약 사항
    - 다대다 관계를 직접 표현할 수 없음
    - 구조가 복잡하고 데이터의 삽입, 삭제, 수정, 검색이 쉽지 않음

<br>
<br>

### Relational Data Model

- 일반적으로 많이 사용되는 논리적 데이터 모델

- 하나의 개체에 대한 데이터를 하나의 Relation (혹은 Table)에 저장

<br>
<br>

### Terms in Relational Data Model

- **Relation**
    - 하나의 개체에 관한 데이터를 2차원 테이블의 구조로 저장한 것
    - 파일 관리 시스템 관점에서 파일에 대응

- **Attribute**
    - Relation의 열, Attribute
    - 파일 관리 시스템 관점에서 필드에 대응

- **Tuple**
    - Relation의 행
    - 파일 관리 시스템 관점에서 레코드에 대응

- **Domain**
    - 하나의 속성이 가질 수 있는 모든 값의 집합
    - 속성 값을 입력 및 수정할 때 적합성의 판단 기준이 됨
    - 일반적으로 속성의 특성을 고려한 데이터 타입으로 정의

- **Null**
    - 속성 값을 아직 모르거나 해당되는 값이 없음을 표현

- **Degree**
    - 하나의 Relation에서 속성의 전체 개수

- **Cardiinality**
    - 하나의 Relation에서 Tuple의 전체 개수

<br>
<br>

### Relation Schema and Relation Instance

- Relation Schema (or Relation Intension)
    - 논리적 구조
    - Relation 이름과 Relation에 포함된 모든 속성 이름으로 정의
        - 예 ) 고객 (고객아이디, 고객이름, 나이, 등급, 직업, 적립금)

- Relation Instance (or Relation Extension)
    - 어느 한 시점에 Relation에 존재하는 Tuple들의 집합

<br>
<br>

### Relation이 모여 Database를 구성

- Database Schema
    - 데이터베이스의 전체 구조
    - 데이터베이스를 구성하는 Relation Schema의 모음

- Database Instance
    - 데이터베이스를 구성하는 Relation Instance의 모음

<br>
<br>

### Relation의 특성

- Tuple의 유일성
    - 하나의 Relation에는 동일한 Tuple이 존재 불가

- Tuple의 무순서
    - 하나의 Relation에서 Tuple 사이의 순서는 무의미

- Attribute의 무순서
    - 하나의 Relation에서 Attribute 사이의 순서는 무의미

- Attribute의 원자성
    - Attribute 값으로 원자 값만 사용 가능 (배열 등의 여러 값 사용 x)

<br>
<br>

### Key in Relation

- Relation에서 Tuple들을 유일하게 구별하는 속성의 집합

- 키의 특성

    - 유일성 (uniqueness)
        
        : 하나의 Relation에서 모든 Tuple은 서로 다른 키 값을 가져야 함
        
    - 최소성 (minimality)
        
        : 꼭 필요한 최소한의 Attribute들로만 키를 구성
        
<br>
<br>

### Super Key vs. Candidate Key vs. Primary Key

- Super key : 유일성을 만족하는 속성(들)
    - 예 ) 고객 릴레이션의 슈퍼키 : 고객 아이디, (고객아이디, 고객이름), (고객이름, 주소) 등

- Candidate key : 유일성과 최소성을 만족하는 속성(들)
    - 예 ) 고객 릴레이션의 후보키 : 고객아이디, (고객이름, 주소) 등

- Primary key : 후보키 중에서 기본적으로 사용하기 위해 선택한 키
    - 예 ) 고객 릴레이션의 기본키 : 고객아이디

<br>
<br>

### Foreign Key

- 다른 Relation의 Primary Key를 참조하는 속성(들)

- Relation들 간의 관계를 표현
    - 참조하는 Relation : Foreign Key를 가진 Relation
    - 참조되는 Relation : Foreign Key가 참조하는 Primary Key를 가진 Relation

- Foreign Key의 Attribute과 그것이 참조하는 Primary Key의 Attribute의 이름은 달라도 되지만 Domain은 같아야 함
    - 도메인은 가질 수 있는 값의 집합

- 하나의 Relation에는 Foreign Key가 여러 개 존재할 수도 있고 Foreign Key를 Primary Key로 사용할 수도 있음

- 같은 Relation의 Primary Key를 참조하는 Foreign Key도 정의할 수 있으며, Foreign Key의 Attribute은 Null 값을 가질 수도 있음

<br>
<br>

### Integrity Constraint

- 데이터의 무결성을 보장하여 일관된 상태로 유지하기 위한 규칙
    - 무결성 : 데이터를 결함이 없는 상태, 즉 정확하고 유효하게 유지하는 것

<br>
<br>

### Entity Integrity Constraint

- Primary Key를 구성하는 모든 Attribute는 Null 값을 가질 수 없는 규칙

<br>
<br>

### Referential Integrity Constraint

- Foreign Key는 참조할 수 없는 값을 가질 수 없는 규칙

- [주의] Foreign Key의 Attribute가 Null 값을 가진다고 해서 참조 무결성 제약조건을 위반한 것은 아님

<br>
<br>
<br>
<br>

# Relational Modeling 과정

<br>

### Rules for Relational Model

- E-R 다이어그램을 Relation 스키마로 변환하는 규칙

    - 규칙 1 : 모든 개체는 Relation으로 변환
    - 규칙 2 : 다대다 관계는 Relation으로 변환
    - 규칙 3 : 일대다 관계는 Foreign Key로 표현
    - 규칙 4 : 일대일 관계는 Foreign Key로 표현
    - 규칙 5 : 다중 값 속성은 Relation으로 변환

- 변환 규칙을 순서대로 적용하되, 해당되지 않는 규칙은 제외함

<br>
<br>

### (규칙 1) 모든 개체는 Relation으로 변환

- 개체의 이름 → Relation 이름

- 개체의 속성 → Relation의 속성

- 개체의 키 속성 → Relation의 Primary Key

- 개체의 속성이 복합 속성인 경우에는
    - 복합 속성을 구성하고 있는 단순 속성만 Relation의 속성으로 변환
    - 혹은 데이터 활용성을 고려해 복합속성을 Relation의 한 속성으로 변환

<br>
<br>

### (규칙 2) 다대다 관계는 Relation으로 변환

- 관계의 이름 → Relation 이름

- 관계의 속성 → Relation의 속성

- 관계에 참여하는 개체를 규칙 1에 따라 Relation으로 변환

- 이 Relation의 Primary Key를 관계 Relation에 포함시켜 Foreign Key로 지정

- 마지막으로 모든 Foreign Key들을 조합하여 관계 Relation의 Primary Key로 지정
    - 혹은 별도 Primary Key를 위한 속성을 추가

<br>
<br>

### (규칙 3-1) 일반적인 일대다 관계는 FK로 표현

- 일대다 관계에서 1측 개체 Relation의 기본키를 n측 개체 Relation에 포함시켜 Foreign Key로 지정

- 관계의 속성들도 n측 개체 Relation에 포함시킴

<br>
<br>

### (규칙 3-2) 약한 개체의 일대다 관계는 FK를 포함해 PK로 지정

- 일대다 관계에서 1측 개체 Relation의 기본키를 n측 개체 Relation에 포함시켜 외래키로 지정

- 관계의 속성들도 n측 개체 Relation에 포함시킴

- n측 개체 Relation은 외래키를 포함하여 기본키를 지정함
    
    (약한 개체는 오너 개체에 따라 존재 여부가 결정되므로 오너 개체의 기본키를 이용해 식별)
   
<br>
<br>
 

### (규칙 4-1) 일반적인 일대인 관계는 FK를 서로 주고 받음

- 관계의 속성들도 모든 개체 Relation에 포함시킴

- 불필요한 데이터 중복이 발생할 수 있음

<br>
<br>

### (규칙 4-2) 필수적으로 참여하는 개체의 Relation만 FK 받음

- 관계의 속성들은 관계에 필수적으로 참여하는 개체 Relation에 포함시킴

<br>
<br>

### (규칙 4-3) 모든 개체가 필수적으로 참여하면 Relation을 하나로 통합

- 관계의 이름을 Relation 이름으로 사용하고 관계에 참여하는 두 개체의 속성들을 관계 Relation에 모두 포함시킴

- 두 개체 Relation의 키 속성을 조합하여 관계 Relation의 Primary Key로 지정

<br>
<br>

### (규칙 5) 다중 값 속성은 Relation으로 변환

- 다중 값 속성과 함께 그 속성을 가지고 있던 개체 Relation의 PK를 FK로 가져와 새로운 Relation에 포함시킴

- 새로운 Relation의 PK는 다중 값 속성과 FK를 조합해 지정

- 만약 다중값 속성을 그대로 개체 Relation에 포함한다면 다중 값을 저장할 수 없는 Relation 특성을 위반

- 그렇다고 개체 Relation에 다중 값 속성 하나 하나를 Tuple로 저장하면 불필요한 데이터 중복 문제 발생

- 별도 Relation으로 만들어 관리하면 데이터 중복 문제 방지 가능

<br>
<br>

### 그밖에 규칙들 …

- 모든 관계를 독립적인 Relation으로 변환 가능
    - 속성이 많은 관계는 유형에 상관없이 릴레이션으로의 변환을 고려할 수 있음
    - 개체가 자기 자신과 관계를 맺는 순환 관계의 경우