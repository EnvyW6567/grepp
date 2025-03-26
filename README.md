# Grepp 시험 예약 시스템

## 🛠 기술 스택

- **백엔드**: FastAPI
- **데이터베이스**: PostgreSQL
- **ORM**: SQLAlchemy
- **인증**: JWT
- **테스트**: Pytest

---

## 📦 프로젝트 구조

```
grepp/
│
├── src/
│   ├── auth/             # 인증 의존성
│   ├── core/             # 핵심 설정 및 유틸리티
│   ├── exam/             # 시험 관련 모델, 서비스, 라우터
│   ├── member/           # 회원 관련 모델, 서비스, 라우터
│   ├── reservation/      # 예약 관련 모델, 서비스, 라우터
│   └── db/               # 데이터베이스 설정
│
├── test/                 # 단위 테스트 디렉토리
│   ├── exam/
│   ├── member/
│   └── reservation/
│
├── docker-compose.yml    # 도커 컴포즈 설정
└── pyproject.toml        # 프로젝트 의존성 및 설정
```

---

## 🚀 시작하기

### 사전 요구사항

- Python 3.11+
- Docker
- poetry

### 설치 및 실행

0. 가상 환경 구축

```bash
python -m venv venv # 버전 3.11 이상
source venv/bin/activate
```

1. 의존성 설치

```bash
poetry install
```

2. 환경 변수 설정

- `.env` 파일을 생성하고 필요한 환경 변수 추가
- 예시)

```
SERVER_PORT=8000

POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=postgres
POSTGRESQL_DATABASE=grepp

SECRET_KEY="asdifjhasljkdfhslakjfdhsdlajkfnaskljdfnsaldkjfnasdlkjfnasjklfnalskjfnkjsladfn"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

3. Postgresql 컨테이너 실행

```bash
docker-compose up -d
```

4. 서버 실행 (default: 8000번 포트)

```bash
python main.py
```

---

## 🧪 테스트

### 프로젝트 테스트 실행

```bash
pytest
```

---

## 📋 API 문서

```
/docs
```

### 테스트 방법

- 토큰 기반 인증을 사용하기 때문에 사용자 생성 후 테스트 필요
- POST /members/create : 사용자 생성
- Authorized 버튼 클릭 후 생성한 사용자 username, password 입력

