### Docker 설치

- Docker 설치
    
    Installer Download - https://docs.docker.com/desktop/install/mac-install/
    
- Rosetta 설치
    
    ```python
    softwareupdate --install-rosetta
    ```
    
    <p align="center"><img width="400" height="70" alt="Untitled (1)" src="https://github.com/user-attachments/assets/3b6d2ee6-b7db-4b7b-a5bb-81334e29f4d6"></p>

    
- Docker 설치 확인
    
    ```python
    docker -v
    ```
    
    <p align="center"><img width="300" height="35" alt="Untitled (1)" src="https://github.com/user-attachments/assets/ab84d39f-1a08-430a-aeed-5fcafef6fa0c"></p>

<br>

### Docker 동작 확인

> **💡 Docker 클라이언트, 도커 호스트, 도커 레지스트리 간 흐름**
> 
> 
> 1. [Client → Docker Host] 클라이언트는 도커 명령어를 사용하여 도커 호스트에 요청을 보냅니다.
> 
> 2. [Docker Host] 도커 호스트는 클라이언트의 요청을 받아들이고, 해당 요청에 따라 컨테이너를 생성, 중지, 제거하거나 이미지를 관리합니다.
> 
> 3. [Docker Host → Registry] 만약 클라이언트가 이미지를 생성하거나 업로드하려면, 도커 호스트는 해당 이미지를 도커 레지스트리에 업로드합니다.
> 
> 4. [Registry] 도커 레지스트리는 이미지를 저장하고 관리하는 중앙 집중식 저장소입니다. 도커 호스트는 도커 레지스트리에 이미지를 업로드하거나 다운로드할 수 있습니다.
> 
> 5. [Docker Host → Client] 컨테이너가 종료되면, 도커 호스트는 해당 컨테이너의 상태와 결과를 클라이언트에게 반환합니다.
> 
> - **이렇게 클라이언트, 도커 호스트, 그리고 도커 레지스트리는 도커 환경에서 상호 작용하며, 이미지의 업로드와 다운로드, 컨테이너의 생성과 관리 등의 작업을 수행합니다.**

<p align="center"><img width="500" height="250" alt="Untitled (1)" src="https://github.com/user-attachments/assets/d981f856-a70d-49c1-a67a-b89531f67041"></p>

<br>


### Docker Image 설치

1. nginx 다운로드
    
    ```python
    # docker hub에서 nginx를 다운로드
    docker pull nginx
    ```
    
    <p align="center"><img width="400" height="150" alt="Untitled (1)" src="https://github.com/user-attachments/assets/17bd4a41-b49e-4702-97b3-b28273fcef1b"></p>
    
    > **docker 이미지로 다운로드할 수 있는 목록**
    
        Ubuntu, CentOS, Alpine, Nginx, MySQL, Redis, Node.js, Python, Java, Ruby, Go, PHP, MongoDB, Postgres, Elasticsearch, Grafana, Jenkins, WordPress, Django, Ruby on Rails, Laravel 등
    
        https://hub.docker.com
    > 
    
2. docker desktop으로 생성된 이미지 중 nginx를 확인
    
    <p align="center"><img width="400" height="150" alt="Untitled (1)" src="https://github.com/user-attachments/assets/861b0d71-a69a-4799-8ef2-afe962bb5cb0"></p>

<br>

### Docker Container 생성 및 실행

1. Docker로 컨테이너를 생성하고 실행.
    
    ```python
    # nginx 이미지를 기반으로 my-nginx 이름의 Docker 컨테이너를 생성하고 실행하는 명령어
    $ docker run -d -p 80:80 --name my-nginx nginx
    ```
    
    - `d` : 컨테이너를 백그라운드에서 실행하는 detached 모드로 실행
    - `p 80:80` : 호스트 머신의 80 포트를 컨테이너의 80 포트로 매핑하여 컨테이너 내에서 실행 중인 NGINX 웹 서버에 접근하도록
    - `-name my-nginx` : 컨테이너에 "my-nginx"라는 이름을 할당
    - `nginx` : 컨테이너를 생성할 때 사용할 Docker 이미지의 이름을 지정
    
    <p align="center"><img width="350" height="10" alt="Untitled (1)" src="https://github.com/user-attachments/assets/05935f15-9c66-4829-9c16-7009f7af3b95"></p>
    
2. 컨테이너 생성 확인
    
    <p align="center"><img width="400" height="130" alt="Untitled (1)" src="https://github.com/user-attachments/assets/bf97685b-f928-4b42-8b31-3f16770dbce8"></p>
    
3. localhost의 80번 포트 - nginx기반 웹 서버 수행 확인
    
    <p align="center"><img width="400" height="145" alt="Untitled (1)" src="https://github.com/user-attachments/assets/971f5203-3c55-438a-97ab-be700a6edc98"></p>

<br>

### Docker Registry 생성

1. Docker Hub 사이트 로그인
2. Repositories  >  click ‘create repository’
3. Repository 생성
    
    <p align="center"><img width="350" height="145" alt="Untitled (1)" src="https://github.com/user-attachments/assets/b9a3c0af-2fc9-4d2d-8ba6-b625b9d5cb80"></p>
    
    - private으로 생성
    
    <p align="center"><img width="350" height="110" alt="Untitled (1)" src="https://github.com/user-attachments/assets/8d941d68-6f50-4ac4-8c58-29c47457e706"></p>
    
4. Terminal에서 docker login
    
    <p align="center"><img width="300" height="40" alt="Untitled (1)" src="https://github.com/user-attachments/assets/d6ca071e-2bce-449b-9126-5d4e1ba36ad2"></p>
    
5. Docker image에 Tag 추가
    
    ```python
    # docker Image 리스트 확인
    $ docker image ls
    ```
    
    <p align="center"><img width="300" height="15" alt="Untitled (1)" src="https://github.com/user-attachments/assets/b407c9e2-949b-4c55-96ee-dbb108275114"></p>
    
    ```python
    # docker image tag format
    $ docker tag <local_image_name>:<tag> <registry_address>/<image_name>:<tag>
    
    # docker tag를 통해 nginx라는 이미지를 dkgus33/my-nginx라는 새롭게 구성한 repository에 1.0이라는 태깅
    $ docker tag nginx dkgus33/my-nginx:1.0
    ```
    
6. Docker Registry Repository에 올리기
    
    ```python
    # docker Registry format
    $ docker push <registry_address>/<image_name>:<tag>
    
    # docker Registry 사용예시
    $ docker push dkgus33/my-nginx:1.0
    ```
    
    <p align="center"><img width="350" height="100" alt="Untitled (1)" src="https://github.com/user-attachments/assets/2f5a0e65-0f8b-4846-9fae-3195ccf25f6b"></p>
    
7. push 결과 확인
    
    <p align="center"><img width="350" height="190" alt="Untitled (1)" src="https://github.com/user-attachments/assets/b0b692c6-1317-4488-942f-c2215ace84dc"></p>

<br>

### Registry 가져오기

1. 기존에 구성한 Registry 가져오기
    
    ```python
    # Docker Registry pull format 
    $ docker pull <registry_address>/<image_name>:<tag>
     
    # Docker Registry pull example
    $ docker pull dkgus33/my-nginx:1.0
    ```
    
    <p align="center"><img width="400" height="90" alt="Untitled (1)" src="https://github.com/user-attachments/assets/5d04ed9a-0b57-4403-bbf9-87fb90c06e08"></p>
    
2. Docker Desktop 확인
    
    <p align="center"><img width="400" height="140" alt="Untitled (1)" src="https://github.com/user-attachments/assets/cc918a62-a167-43aa-966c-b1bbdc610e7b"></p>

    <br>
    
    | **docker 명령어** | **설명** |
    | --- | --- |
    | docker -v | docker 버전을 확인합니다. |
    | docker ps -a | docker의 컨테이너 목록을 확인합니다. |
    | docker pull [docker image] | docker의 이미지를 다운로드 받습니다. |
    | docker build | docker 이미지를 빌드합니다. |
    | docker push | docker 이미지를 레지스트리에 업로드합니다. |
    | docker run | docker 이미지를 기반으로 컨테이너를 생성하고 실행시킵니다. |
    | docker login | docker 계정 로그인을 수행합니다. |
    | docker image ls | docker 이미지 목록들을 확인합니다. |
    | docker tag | docker 이미지에 이름 또는 태그를 할당합니다. |
    | docker pull | docker 이미지를 레지스트리에서 가져옵니다. |
