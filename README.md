# BOVI - 보드게임 채팅봇 🎲

Django로 개발된 보드게임 전용 채팅봇 웹 애플리케이션입니다.

## 🎯 주요 기능

### 1. 🎮 게임 추천
- **RAG 기반 추천**: 사용자 요청에 맞는 맞춤형 보드게임 추천
- **파인튜닝 모델**: 전문적으로 학습된 GPT 모델 사용
- 실시간 채팅 인터페이스

### 2. 🤖 GPT 룰 설명
- **게임별 QA DB**: 10여개 인기 보드게임 지원
- **친근한 설명**: 초보자도 이해하기 쉬운 룰 설명
- **실시간 Q&A**: 궁금한 룰에 대한 즉석 질문답변
- **QR코드 모바일 지원**: 비밀 질문 가능

### 3. ⚙️ 파인튜닝 룰 설명
- **전문 AI 모델**: 보드게임 전문 데이터로 학습된 모델
- **정확한 설명**: 복잡한 규칙과 예외 상황까지 상세 설명
- **전문가 수준**: 공식 룰북 수준의 정확성
- **QR코드 모바일 지원**: 비밀 질문 가능

## 🗄️ 데이터베이스 구조

### **GPTRuleQA 모델**
- `id`: 번호 (PK, 오토인크리먼트)
- `game_name`: 게임 이름 (인덱스)
- `question`: 질문 내용
- `answer`: 답변 내용
- `created_at`, `updated_at`: 생성/수정 시간

### **FinetuningRuleQA 모델**
- `id`: 번호 (PK, 오토인크리먼트)
- `game_name`: 게임 이름 (인덱스)
- `question`: 질문 내용
- `answer`: 답변 내용
- `created_at`, `updated_at`: 생성/수정 시간

## 🚀 로컬 개발 환경 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 데이터베이스 설정
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. 샘플 QA 데이터 로드
```bash
python manage.py load_qa_data
```

### 4. 관리자 계정 생성
```bash
python manage.py createsuperuser
```

### 5. 서버 실행
```bash
python manage.py runserver
```

웹 브라우저에서 `http://127.0.0.1:8000/`에 접속하여 사용할 수 있습니다.

## 🌐 EC2 배포

**EC2 배포가 필요하신가요?** 
상세한 가이드는 `EC2_DEPLOY_GUIDE.md` 파일을 참고하세요!

### 주요 배포 단계:
1. EC2 인스턴스 생성 (Ubuntu 22.04)
2. PostgreSQL 설치 및 설정
3. 프로젝트 업로드
4. 환경변수 설정 (.env)
5. Gunicorn + Nginx 설정
6. QA 데이터 로드

## 📱 모바일 QR 기능

### GPT 룰 설명 & 파인튜닝 룰 설명
1. 해당 페이지로 이동
2. 페이지 하단의 QR코드를 스마트폰으로 스캔
3. 모바일에서 게임 선택 후 비밀스럽게 질문 가능
4. **보드게임 중 다른 플레이어들에게 들키지 않고 룰 확인!**

## 🎲 지원 게임 목록

현재 다음 게임들을 지원합니다:
- 카탄
- 스플렌더  
- 아줄
- 윙스팬
- 뱅
- 킹 오브 도쿄
- 7 원더스
- 도미니언
- 스몰 월드
- 티켓 투 라이드

## 🗄️ QA 데이터 관리

### Django 관리자 패널
```
http://127.0.0.1:8000/admin/
```

### QA 데이터 추가/수정
1. **GPT Rule QAs** → GPT 룰 설명용 질문답변
2. **Finetuning Rule QAs** → 파인튜닝 룰 설명용 질문답변

### 대량 데이터 관리 (Django Shell)
```bash
python manage.py shell
```

```python
from chatbot.models import GPTRuleQA, FinetuningRuleQA

# 새 QA 추가
GPTRuleQA.objects.create(
    game_name="테라포밍 마스",
    question="테라포밍 마스 기본 룰은?",
    answer="화성을 테라포밍하는 게임입니다..."
)

# 게임별 QA 조회
catan_qas = GPTRuleQA.objects.filter(game_name="카탄")
for qa in catan_qas:
    print(f"Q: {qa.question}")
    print(f"A: {qa.answer}")
```

## 📁 프로젝트 구조

```
boardgame_chatbot/
├── boardgame_chatbot/          # 프로젝트 설정
│   ├── settings.py            # DB 및 환경변수 설정
│   └── urls.py               
├── chatbot/                    # 메인 앱
│   ├── models.py              # GPTRuleQA, FinetuningRuleQA
│   ├── views.py               # API 엔드포인트
│   ├── urls.py                # URL 라우팅
│   ├── admin.py               # QA 관리자 설정
│   └── management/commands/   # 관리 명령어
│       └── load_qa_data.py    # 샘플 데이터 로드
├── templates/                  # HTML 템플릿
├── static/                     # 정적 파일
├── requirements.txt           # 의존성 목록
├── EC2_DEPLOY_GUIDE.md        # EC2 배포 가이드
└── .env.example               # 환경변수 예시
```

## 🌐 API 엔드포인트

- `POST /api/chat/` - 채팅 메시지 처리
- `POST /api/rule-summary/` - 게임 룰 요약
- `GET /api/qr/<chat_type>/` - QR코드 생성
- `GET /mobile/<chat_type>/` - 모바일 채팅 페이지

## 🔧 환경변수 설정

`.env` 파일 생성:
```bash
cp .env.example .env
```

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://user:password@localhost:5432/boardgame_db  # EC2용
OPENAI_API_KEY=your-openai-api-key-here
FINETUNING_MODEL_ID=ft:gpt-3.5-turbo-0125:tset::BX2RnWfq
```

## 🤖 AI 모델 구조

### **게임 추천**
- **모델**: 파인튜닝된 GPT-3.5-turbo
- **방식**: RAG (Retrieval-Augmented Generation)
- **특징**: 사용자 요청 → 벡터 검색 → 컨텍스트 기반 추천

### **룰 설명** 
- **모델**: 파인튜닝된 GPT-3.5-turbo
- **방식**: QA 데이터베이스 우선 검색 → 실시간 AI 응답
- **특징**: 
  - GPT 룰 설명: 친근하고 이해하기 쉬운 설명
  - 파인튜닝 룰 설명: 전문적이고 정확한 설명

## 🎯 사용 플로우

1. **홈페이지** → 3개 기능 선택
2. **게임 추천**: 바로 질문 가능
3. **룰 설명**: 게임 선택 → 룰 요약 확인 → 세부 질문
4. **모바일**: QR코드 → 게임 선택 → 비밀 질문

## 💾 데이터베이스 확인 방법

### 1. Django 관리자 패널 (추천)
```
http://127.0.0.1:8000/admin/
```

### 2. Django Shell
```bash
python manage.py shell
```

```python
from chatbot.models import GPTRuleQA, FinetuningRuleQA

# 전체 QA 개수 확인
print(f"GPT QA: {GPTRuleQA.objects.count()}개")
print(f"파인튜닝 QA: {FinetuningRuleQA.objects.count()}개")

# 게임별 QA 확인
for qa in GPTRuleQA.objects.all()[:5]:
    print(f"{qa.id}: {qa.game_name} - {qa.question[:30]}...")
```

### 3. 명령어로 QA 통계 확인
```bash
python manage.py load_qa_data  # 기존 데이터 + 통계 출력
```

## ✅ 개발 완료 체크리스트

- [x] Django 프로젝트 구조 완성
- [x] QA 데이터베이스 모델 (GPTRuleQA, FinetuningRuleQA)
- [x] 파란색 테마 웹 인터페이스
- [x] 3개 주요 기능 (게임추천, GPT룰, 파인튜닝룰)
- [x] QR코드 모바일 지원
- [x] 관리자 패널 QA 관리
- [x] 샘플 데이터 로드 명령어
- [x] EC2 배포 준비 (PostgreSQL, Gunicorn, Nginx)
- [x] 환경변수 기반 설정

## 🚀 다음 단계

1. **로컬 테스트 완료**
2. **EC2 인스턴스 생성**
3. **실제 OpenAI API 키 연동**
4. **QA 데이터 대량 입력**
5. **도메인 연결 및 SSL 설정**

---

**🎉 BOVI 프로젝트 완성!** 
EC2 배포가 필요하시면 `EC2_DEPLOY_GUIDE.md`를 참고하세요! 🚀
# bovi_django
