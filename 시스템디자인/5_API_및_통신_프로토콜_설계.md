## 5단계 : API 및 통신 프로토콜 설계

<br>

API(Application Programming Interface) 및 통신 프로토콜을 설계하면 시스템의 다양한 구성 요소가 서로 상호 작용하는 방식과 외부 클라이언트가 시스템의 기능에 액세스할 수 있는 방법이 정의된다.

<br>

## API 요구사항 식별 :

- API를 통해 시스템이 노출해야 하는 주요 기능과 서비스를 결정한다.
- API와 상호작용할 다양한 유형의 클라이언트(예 : 웹, 모바일, 서드파티 서비스)를 고려한다.
- 각 API 엔드포인트에 대한 데이터 입력, 출력 및 특정 요구사항을 식별한다.

<br>

## API 스타일 선택 :

- 시스템 요구사항과 클라이언트 요구사항에 따라 적절한 API 스타일을 선택한다
- RESTful API(Representational State Transfer)는 웹 기반 시스템에 일반적으로 사용되며 리소스 조작을 위한 균일한 인터페이스를 제공한다.
- GraphQL API는 클라이언트가 특정 데이터 필드를 쿼리하고 검색할 수 있는 유연하고 효율적인 방법을 제공한다.
- RPC(Remote Procedure Call) API는 잘 정의된 프로시저 또는 함수가 있는 시스템에 적합하다.

<br>

## API 엔드포인트 정의 :

예 ) Twitter API

    createProfile(name, email, password)
    login(email, password)
    postTweet(userId, content, timestamp)
    followUser(userId1, userId2)

- 시스템의 기능과 데이터 모델을 기반으로 명확하고 직관적인 API 엔드포인트를 설계한다.
- 원하는 작업을 나타내기 위해 각 엔드포인트를 적절한 HTTP 메서드(예 : GET, POST, PUT, DELETE)를 사용한다.

<br>

## 데이터 형식 지정 :

- API 요청 및 응답에 대한 데이터 형식을 선택한다. 일반적인 형식으로는 JSON(JavaScript Object Notation)과 XML(eXtensible Markup Language)이 있다.
- 클라이언트 및 시스템 구성 요소와의 가독성, 파싱 효율성 및 호환성과 같은 요소를 고려한다.

<br>

## 통신 프로토콜 선택 :

- **HTTP** : RESTful API 및 웹 기반 통신에 일반적으로 사용된다.
- **WebSockets** : 클라이언트와 서버 간의 실시간 양방향 통신에 유용하다. (예 : 채팅 애플리케이션)
- **gRPC(gRPC Remote Procedure Call)** : 마이크로서비스 아키텍처에서 서비스 간 통신에 효율적이다.
- **메시징 프로토콜** : 비동기 메시징을 위한 AMQP, MQTT(메시지 큐와 함께 자주 사용됨)