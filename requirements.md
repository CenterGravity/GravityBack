# Gravity Backend API 요구사항

중력 프로젝트 API를 구축하기 위해 `main.py`, `routers/`, `utils/` 중심으로 필요한 구현 요구사항을 정리했습니다. MySQL + FastAPI + SQLAlchemy 기반입니다.

## 목표
- 사용자 인증/인가, 게시글, 시뮬레이션, 좋아요 기능을 제공하는 REST API.
- 공개/비공개 콘텐츠에 대한 접근 제어 및 JWT 기반 인증.
- Swagger UI(`/docs`)와 ReDoc(`/redoc`)로 문서 확인 가능.

## 디렉터리/모듈 역할
- `main.py`: FastAPI 앱 생성, DB 연결 확인, 라우터 등록, 전역 설정(CORS, 이벤트 훅).
- `routers/__init__.py`: 공통 `APIRouter` 생성 및 각 라우터 모듈 포함.
- `routers/auth.py`: 회원가입, 로그인, 토큰 발급/검증.
- `routers/user.py`: 사용자 조회, 내 정보 조회/수정.
- `routers/articles.py`: 게시글 CRUD, 공개/비공개 처리.
- `routers/simulations.py`: 시뮬레이션 CRUD, 공개 처리, 좋아요.
- `utils/dependencies.py`: DB 세션 의존성 및 공통 의존성.
- `utils/security.py`: 비밀번호 해시/검증, JWT 발급/파싱, 현재 사용자 조회 의존성.
- `models/`: SQLAlchemy ORM 모델(이미 정의됨).
- `schemas/`: Pydantic 요청/응답 스키마.
- `test_main.http`: 수동 테스트용 HTTP 샘플.

## main.py 요구사항
- `FastAPI(title, version, openapi_tags)` 초기화; 환경 변수로 CORS 허용 도메인 설정.
- `@app.on_event("startup")`: DB 연결 확인 로그 + 필요 시 `Base.metadata.create_all(bind=engine)` 옵션 처리.
- 전역 미들웨어/예외 처리: DB 세션 정리, 500/404/401 공통 메시지.
- `GET /`: 헬스체크 응답 유지.
- `app.include_router(router, prefix="/api")` 형태로 `routers.router` 등록.

## utils
- `dependencies.py`:
  - `get_db()` 제너레이터: `SessionLocal()` 생성 후 `yield`, `finally`에서 `close()`.
  - 공통 의존성: 페이지네이션 파라미터, 검색어 파라미터 등 필요 시 추가.
- `security.py`:
  - `pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")`.
  - `hash_password`, `verify_password` 제공.
  - `create_access_token(data, expires_delta)` JWT 생성(`python-jose`), 만료 기본 30분.
  - `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")`.
  - `get_current_user`: 토큰 디코드 → `user_id/email`로 DB 조회 → 비활성/삭제 여부 확인 → `User` 반환; 실패 시 401.

## routers 공통
- `routers/__init__.py`에서 `router = APIRouter(prefix="/api")` 생성 후 각 모듈 라우터를 `include_router`.
- 각 라우터 모듈에서 `router = APIRouter(prefix="...")` 정의, `tags` 지정, 필요한 경우 `dependencies=[Depends(get_db)]` 또는 함수 내부 `Depends`.
- 모든 엔드포인트에 `response_model` 지정, `status_code` 명시.
- 예외 시 `HTTPException`으로 4xx/5xx 일관 응답(메시지는 한글 가능).

### 인증 (`routers/auth.py`)
- `POST /auth/register`: `schemas.user.UserCreate` 입력; 이메일 중복 검사 후 유저 생성(비밀번호 해시). 생성된 사용자 정보 또는 토큰 반환(201).
- `POST /auth/login`: `schemas.auth.UserLogin` 입력; 이메일/비밀번호 검증 후 `schemas.auth.Token` 반환(액세스 토큰, bearer).
- (선택) `POST /auth/refresh` 토큰 재발급, `POST /auth/logout` 블랙리스트 처리 여부 정의.

### 사용자 (`routers/user.py`)
- `GET /users/me`: 인증 필요; 현재 사용자 정보 반환.
- `GET /users/{user_id}`: 공개 프로필 조회; 없으면 404.
- (선택) `PATCH /users/me`: username/email 변경 시 비밀번호 재확인; 중복 이메일 차단.
- 응답 DTO 예시: `UserResponse`(id, username, email, created_at, article_count, simulation_count, like_count 등).

### 게시글 (`routers/articles.py`)
- `POST /articles`: 인증 필요; `ArticleCreate(title, content, is_public)` 수신 후 저장, `Articleresponse(articleId)` 또는 상세 응답 반환.
- `GET /articles`: 공개 글 목록 페이지네이션(`page`, `size`), 정렬 옵션(최신/제목), 검색어(`q`) 필터.
- `GET /articles/{article_id}`: 공개 글 또는 작성자 본인만 접근 가능.
- `PATCH /articles/{article_id}`: 작성자만 수정; `ArticleUpdate`.
- `DELETE /articles/{article_id}`: 작성자만 삭제; 204 반환.

### 시뮬레이션 (`routers/simulations.py`)
- `POST /simulations`: 인증 필요; `simulationResiter(title, data, data2, is_public)` 저장, `owner_id`=현재 사용자.
- `GET /simulations`: 공개 목록 페이지네이션; 정렬 옵션(최신/좋아요순); 검색어 옵션 필요 시 추가.
- `GET /simulations/{simulation_id}`: 공개 또는 소유자 접근; 좋아요 수 포함.
- `PATCH /simulations/{simulation_id}`: 소유자만 수정; 제목/데이터/공개 여부 변경.
- `POST /simulations/{simulation_id}/like`: 인증 필요; `SimulationLike` 유니크 제약 준수, 중복 시 409, 성공 시 총 좋아요 수 반환.
- `DELETE /simulations/{simulation_id}/like`: 본인 좋아요 취소; 없으면 404.

## 스키마/모델 정합성
- Pydantic 클래스 명은 `UserCreate`, `ArticleCreate`, `ArticleUpdate`, `SimulationCreate`, `SimulationResponse`, `Token` 등 UpperCamelCase로 정리.
- 응답 DTO에 `id`, `created_at`, `updated_at` 포함; 비밀번호 해시 등 민감 정보 제외.
- 현재 `models/simulation.py`와 `models/simulation_like.py`의 클래스가 뒤바뀌어 있으므로 임포트 시 주의하거나 파일을 재배치.

## 에러/상태 코드 규칙
- 401: 인증 실패/토큰 불량, 403: 권한 없음, 404: 리소스 없음, 409: 중복 좋아요/이메일 등, 422: 유효성 오류, 500: 기타 서버 오류.

## 테스트
- `test_main.http`에 시나리오 추가: 회원가입 → 로그인 → 토큰으로 글 생성 → 글 조회 → 시뮬레이션 생성 → 좋아요 → 좋아요 취소.
- 가능하면 pytest 기반 단위/통합 테스트 추가(옵션).

## 운영 관련
- 환경 변수: `DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `CORS_ORIGINS`.
- `docker-compose.yml`의 DB 서비스와 연동 시 `DATABASE_URL` 구성 확인.
