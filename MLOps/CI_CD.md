## CI/CD 란

CI/CD는 지속적 통합(Continuous Integration) 및 지속적 제공/배포(Continuous Delivery/Deployment)를 의미하며, 소프트웨어 개발 라이프사이클을 간소화하고 가속화하는 것을 목표로 한다.

<br>

### CI/CD 파이프라인

![스크린샷 2024-09-13 오후 5 07 47](https://github.com/user-attachments/assets/30a33b4b-1532-4504-84dd-33dd364eccd3)

<br>

### 지속적 통합(CI)

코드 변경 사항을 공유 소스 코드 레포지토리에 자동으로 자주 통합하는 사례를 나타낸다. 업데이트가 이루어지면 병합된 코드 변경 사항의 신뢰성을 보장하기 위해 자동화된 테스트 단계가 트리거된다.

- 동시에 개발 중인 애플리케이션의 분기가 너무 많아 상호 충돌할 가능성이 있는 문제에 대한 해결책으로 CI를 고려할 수 있다.

**성공적인 CI란?**

    개발자가 애플리케이션에 적용한 변경 사항들이 병합된 후 이러한 변경 사항이 애플리케이션을 손상시키지 않도록 자동으로 애플리케이션을 빌드하고 다양한 수준의 자동화된 테스트를 실행하여 해당 변경 사항을 검증하는 것이다.

    - 클래스, 기능부터 여러 모듈에 이르기까지 모든 것을 테스트한다.
    - 자동화된 테스트를 통해 새 코드와 기존 코드 간 충돌이 발견되는 경우 CI를 적용하면 해당 버그를 빠르게, 자주 수정하기가 더 용이해진다.

<br>

### 지속적 제공/배포 (CD)

코드 변경 사항의 통합, 테스트, 제공을 나타내는 프로세스로, 두 가지 부분으로 구성된다. 지속적 제공(Continuous Delivery) 및 지속적 배포(Continous Deployment)를 의미하며 이 두 용어는 상호 교환하여 사용된다.

**지속적 제공**

    : CI에서 빌드와 단위 및 통합 테스트를 자동화한 다음 검증된 코드를 레포지토리로 릴리즈하는 것을 자동화한다. 

    - 코드 변경 사항의 병합부터 프로덕션 레디 빌드의 제공에 이르기까지 모든 단계에 테스트 자동화와 코드 릴리스 자동화가 수반된다.

**지속적 배포**

    : 지속적 제공의 확장으로, 개발자의 변경 사항을 레포지토리에서 프로덕션으로 릴리스하는 것을 자동화하여 고객이 사용할 수 있도록 하는 것을 말한다.

    - 수동 프로세스로 인한 운영 팀의 업무 과다 문제를 해결
    - 파이프라인의 다음 단계를 자동화함으로써 지속적 제공의 장점을 활용

프로덕션 이전의 파이프라인 단계에는 수동 게이트가 없으므로 지속적 배포는 잘 설계된 테스트 자동화에 크게 의존한다.

- CI/CD 파이프라인에서 다양한 테스트 및 릴리스 단계를 수용하기 위해 자동화된 테스트를 작성해야 하므로 지속적 배포에는 많은 선행 투자가 필요하다.

<br>

### CI/CD의 중요성

- 조직이 버그 및 코드 오류를 예방하는 동시에 지속적인 소프트웨어 개발 및 업데이트 주기를 유지
- 애플리케이션이 커짐에 따른 복잡성을 줄이고 효율성을 높이며 워크플로우를 간소화
- 다운타임 최소화, 코드 릴리스 주기 단축

<br>

### CI/CD와 DevOps 비교

CI/CD와 DevOps는 모두 코드 통합 프로세스를 자동화하는 데 중점을 두어 사용자에게 사치를 제공할 수 있는 프로덕션 환경에서 아이디어가 개발에서 배포 단계로 이동하는 프로세스를 가속화한다.

- DevSecOps
    
    : 전체 IT 라이프사이클에 걸쳐 보안을 통합하는 방식으로 책임을 공유하는 문화, 자동화 및 플랫폼 설계에 대한 접근 방식이다.
    
    - 핵심 구성 요소 : 보안 CI/CD 파이프라인의 도입

<br>

### CI/CD 보안이란

CI/CD 보안은 자동화된 검사 및 테스트로 코드 파이프라인을 보호하여 소프트웨어 제공 시 취약점을 방지하는 데 사용된다. 

- shift-left와 shift-right 접근 방식 등을 통해 기업의 파이프라인에 통합하는 것은 코드를 공격에서 보호하고 데이터 누출을 방지하며 정책을 준수하고 품질 보증을 보장하는 데 도움이 된다.

<br>

### 일반적인 CI/CD 툴

- Jenkins
- Spinnaker
- GoCD
- Concourse
- Screwdriver

<br>
<br>

reference - https://www.redhat.com/ko/topics/devops/what-is-ci-cd