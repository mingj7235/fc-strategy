# FC Strategy Coach

FC Online 전적 분석 및 전략 코칭 웹 애플리케이션

## 프로젝트 개요

Nexon의 FC Online Open API를 활용하여 유저들에게 데이터 기반의 전술 코칭과 플레이 스타일 개선 제안을 제공하는 서비스입니다.

### 주요 기능

- 유저 검색 및 전적 조회
- 슈팅 히트맵 시각화
- 플레이 스타일 분석
- 경기별 상세 통계
- 맞춤형 피드백 제공

## 기술 스택

### Backend
- Python 3.11+
- Django 5.2+ & Django REST Framework
- PostgreSQL
- Redis
- pandas, numpy

### Frontend
- React 19+ with TypeScript
- Vite
- Tailwind CSS
- Recharts, D3.js
- Axios

## 시작하기

### 사전 요구사항

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis (optional, for caching)
- Nexon Open API Key

### Backend 설정

1. 가상환경 생성 및 활성화
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 패키지 설치
```bash
pip install -r requirements.txt
```

3. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 열어 필요한 값들을 설정하세요
```

4. 데이터베이스 설정
```bash
# PostgreSQL 데이터베이스 생성
createdb fc_strategy_db

# 마이그레이션 실행
python manage.py makemigrations
python manage.py migrate
```

5. 슈퍼유저 생성 (선택사항)
```bash
python manage.py createsuperuser
```

6. 개발 서버 실행
```bash
python manage.py runserver
```

Backend API는 `http://localhost:8000`에서 실행됩니다.

### Frontend 설정

1. 디렉토리 이동 및 패키지 설치
```bash
cd frontend
npm install
```

2. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 열어 API URL을 설정하세요
```

3. 개발 서버 실행
```bash
npm run dev
```

Frontend는 `http://localhost:5173`에서 실행됩니다.

## API 엔드포인트

### User APIs
- `GET /api/users/search/?nickname={nickname}` - 유저 검색
- `GET /api/users/{ouid}/matches/` - 유저 매치 목록

### Match APIs
- `GET /api/matches/{match_id}/detail/` - 매치 상세 정보
- `GET /api/matches/{match_id}/heatmap/` - 슈팅 히트맵 데이터

### Stats APIs
- `GET /api/stats/user/{ouid}/` - 유저 통계

## 프로젝트 구조

```
fc-strategy/
├── backend/                    # Django 백엔드
│   ├── api/                   # 메인 API 앱
│   │   ├── models.py          # 데이터 모델
│   │   ├── serializers.py     # DRF Serializers
│   │   ├── views.py           # API Views
│   │   └── analyzers/         # 데이터 분석 로직
│   ├── nexon_api/             # Nexon API 통합
│   │   ├── client.py          # API 클라이언트
│   │   ├── metadata.py        # 메타데이터 로더
│   │   └── exceptions.py      # 커스텀 예외
│   └── fc_strategy/           # Django 프로젝트 설정
│
├── frontend/                   # React 프론트엔드
│   ├── src/
│   │   ├── pages/             # 페이지 컴포넌트
│   │   ├── components/        # 재사용 가능한 컴포넌트
│   │   ├── services/          # API 서비스
│   │   ├── types/             # TypeScript 타입 정의
│   │   └── utils/             # 유틸리티 함수
│   └── package.json
│
└── README.md
```

## 개발 로드맵

### Phase 1: MVP (현재)
- [x] 프로젝트 초기 설정
- [x] 기본 API 구조
- [ ] Nexon API 통합 완성
- [ ] 슈팅 히트맵 구현
- [ ] 기본 통계 대시보드

### Phase 2: 분석 기능
- [ ] AI 코칭 및 약점 진단
- [ ] 승/패 패턴 분석
- [ ] 주간 리포트

### Phase 3: 고급 기능
- [ ] 랭커 벤치마킹
- [ ] 이적시장 분석
- [ ] ML 기반 예측

## 기여하기

이 프로젝트는 개인 프로젝트입니다. 버그 리포트나 기능 제안은 이슈로 등록해 주세요.

## 라이센스

MIT License

## 참고 자료

- [NEXON Open API 공식 문서](https://openapi.nexon.com/ko/game/fconline/)
- [FC Online 매치 정보 좌표 안내](https://openapi.nexon.com/ko/support/notice/2430740/)
