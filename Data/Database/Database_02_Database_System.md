## Database System

- 데이터베이스 시스템은 크게 (1) 사용자, (2) 데이터 언어, (3) 데이터베이스 관리 시스템, (4) 데이터베이스로 구성

<br>
<br>

### Architecturues of Database
    
#### ANSI-SPARC Architecture for Databases
    
    - 미국 표준화 기관인 ANSI/SPARC에서 제안
    - 3단계로 Database를 구조화
        - 내부 단계
            - 물리적인 저장 장치의 관점
        - 개념 단계
            - 조직 전체의 관점
        - 외부 단계
            - 개별 사용자 관점
    
    각 단계별로 다른 추상화 제공
    
    - 내부 단계에서 외부 단계로 갈수록 추상화 레벨이 높아짐
    
<br>

#### Schema vs. Instance
    
    - 데이터베이스에 저장되는 데이터 구조와 제약조건을 정의한 것을 스키마라 부름
        - 각 단계마다 스키마 존재
    - 이와 대비되는 개념으로, 스키마에 따라 데이터베이스에 실제로 저장된 값을 인스턴스라 부름
    
<br>

#### External Level
    
    - External Schema
        - 외부 단계에서 사용자에게 필요한 데이터베이스를 정의한 것
        - 각 사용자가 생각하는 데이터베이스의 모습, 즉 논리적 구조로 사용자마다 다름
        - Sub Schema라고도 부름
    
    하나의 데이터베이스에 여러 External Schema 존재 가능
    
<br>

#### Conceptual Level
    
    - Conceptual Schema
        - 개념 단계에서 데이터베이스 전체의 논리적 구조를 정의한 것
        - 조직 전체의 관점에서 생각하는 데이터베이스의 모습
        - 전체 데이터베이스에 어떤 데이터가 저장되는지, 데이터들 간 어떤 관계가 존재하고 어떤 제약조건이 존재하는지에 대한 정의
        - 데이터에 대한 보안 정책이나 접근 권한에 대한 정의도 포함
    
    데이터베이스 하나에 Conceptual Schema가 하나만 존재함
    
<br>

#### Internal Level
    
    - Internal Schema
        - 전체 데이터베이스가 저장 장치에 실제로 저장되는 방법을 정의
        - 구조, 크기, 접근 경로 등 물리적 저장 구조를 정의
    
    데이터베이스 하나에 Internal Schema가 하나만 존재함
    
<br>
    
#### Data Dependency and Mapping
    
    - 3단계 데이터베이스 구조에서 각 단계는 서로 연결됨
    - 때문에, 데이터 종속성 문제 발생
        - 만약 어떤 하나의 구조가 변경되면, 그것을 참조하고 있던 상/하위 단계의 구조가 영향을 받게 됨
    - 이를 해결하기 위해 사상(Mapping) 기법을 적용
        - 단계와 단계 사이에 중간 Interface를 만들어 놓음
    
<br>
    
#### Mapping
    
    - 단계별 Schema 사이의 대응 관계를 정의함으로써 데이터 독립성을 확보함
        - External-Conceptual Mapping
            - Application Interface라고도 부름
        - Conceptual-Internal Mapping
            - Storage Interface라고도 부름
    
<br>
    
#### Data Independency
    
    - 하위 Schema를 변경하더라도 상위 Schema가 영향을 받지 않는 특성을 일컫는 말
        - External-Conceptual Mapping → Logical Data Independency
            - Conceptual Schema가 변경돼도 External Schema는 영향을 받지 않음
            - Conceptual Schema가 변경되면 관련된 External-Conceptual Mapping만 정확하게 수정하면 됨
        - Conceptual-Internal Mapping → Physical Data Independency
            - Internal Schema 가 변경돼도 Conceptual Schema는 영향 받지 않음
            - Internal Schema가 변경되면 관련된 Conceptual-Internal Mapping만 정확하게 수정하면 됨


<br>
<br>


### Database Management System
    
#### Database Management System (DBMS)
    
    - 파일 시스템의 문제를 해결하기 위해 제시된 소프트웨어
    - 조직에 필요한 데이터를 데이터베이스에 통합하여 저장하고 관리
    
<br>
    
#### Key Functions of DBMS
    
    | 데이터 정의(Definition) | 데이터의 구조를 정의하고 데이터 구조에 대한 삭제 및 변경 기능을 수행항 |
    | --- | --- |
    | 데이터 조작(Manipulation) | 데이터를 조작하는 소프트웨어(응용 프로그램)가 요청하는 데이터의 삽입, 수정, 삭제 작업을 지원함 |
    | 데이터 추출(Retrieve) | 사용자가 조회하는 데이터 혹은 응용 프로그램의 데이터를 추출함 |
    | 데이터 제어(Control) | 데이터베이스 사용자를 생성하고 모니터링하며 접근을 제어함.
    백업과 회복, 동시성 제어 등의 기능을 지원함. |
    
<br>
    
#### Pros and Cons of DBMS
    
    장점
    
    - 데이터 중복을 통제할 수 있다
    - 데이터 독립성이 확보된다
    - 데이터를 동시 공유할 수 있다
    - 데이터 보안이 향상된다
    - 데이터 무결성을 유지할 수 있다
    - 표준화할 수 있다
    - 장애 발생 시 회복이 가능하다
    - 응용 프로그램 개발 비용이 줄어든다
    
    단점
    
    - 비용이 많이 든다
    - 백업과 회복 방법이 복잡하다
    - 중앙 집중 관리로 인한 취약점이 존재한다
    
<br>
    
#### Data Model
    
    - 데이터베이스 시스템에서 현실 세계를 표현한 결과물
        - 계층 데이터 모델 (hierarchical data model)
        - 네트워크 데이터 모델 (network data model)
        - 객체 데이터 모델 (object data model)
        - 관계 데이터 모델 (relatioinal data model)
            - 가장 많이 사용하는 모델
        - 객체-관계 데이터 모델 (object-relational data model)
    
<br>
    
#### 1st Generation of Data Model
    
    - Network DBMS
        
        : 그래프 형태로 구성
        
        - 예 ) IDS (Intergrated Data Store)
    - Hierarchical DBMS
        
        : 트리 형태로 구성
        
        - 예 ) IMS (Information Management System)
    
    포인터 사용
    
<br>
    
#### 2nd Generation of Data Model
    
    - Relational DBMS : 데이터베이스를 테이블 형태로 구성
        - 예 ) MS SQL 서버, Access, Informix, MySQL
        - 속성 값 사용
    - Object Relational DBMS
        - 객체 식별자를 이용

<br>
<br>
    
### Database Users
    - 데이터베이스를 이용하기 위해 접근하는 모든 사람
    - 이용 목적에 따라 데이터베이스 관리자, 최종 사용자, 응용 프로그래머로 구분
    
<br>
    
- 일반 사용자

    - 은행의 창구 혹은 관공서의 민원 접수처 등에서 데이터를 다루는 업무를 하는 사람
    - 프로그래머가 개발한 프로그램을 이용하여 데이터베이스에 접근 일반인

- 응용프로그래머
    - 일반 사용자가 사용할 수 있도록 프로그램을 만드는 사람
    - 자바, C, JSP 등 프로그래밍 언어와 SQL을 사용하여 일반사용자를 위한 UI와 데이터를 관리하는 응용 로직을 개발

- SQL사용자
    - SQL을 사용하여 업무를 처리하는 IT 부서의 담당자
    - 응용 프로그램으로 구현되어 있지 않은 업무를 SQL을 사용하여 처리

- 데이터베이스 관리자(DBA, Database Administrator)
    - 데이터베이스 운영 조직의 데이터베이스 시스템을 총괄하는 사람
    - 데이터 설계, 구현, 유지보수의 전 과정을 담당
    - 데이터베이스 사용자 통제, 보안, 성능 모니터링, 데이터 전체 파악 및 관리, 데이터 이동 및 복사 등 제반 업무를 함
    

    <p align="center"><img width="300" height="100" alt="Untitled (1)" src="https://github.com/user-attachments/assets/99229f23-6f28-4aff-a4ca-ab9a000281d4"></p>
    
<br>
<br>

### Data Language
    - 사용자와 데이터베이스 관리 시스템 간의 통신 수단
    - 사용 목적에 따라 데이터 정의어, 데이터 조작어, 데이터 제어어로 구분