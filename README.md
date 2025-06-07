# 🎲 BOVI 보드게임 채팅봇

Django 기반 보드게임 규칙 설명 및 추천 챗봇

## ⚡ 빠른 시작

### 로컬 개발
```bash
git clone https://github.com/yourusername/boardgame_chatbot.git
cd boardgame_chatbot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### EC2 배포 (Ubuntu)
```bash
# 1. EC2에서 프로젝트 클론
git clone https://github.com/yourusername/boardgame_chatbot.git
cd boardgame_chatbot

# 2. 자동 배포 스크립트 실행
chmod +x deploy_ec2.sh
./deploy_ec2.sh

# 3. 관리자 계정 생성
source venv/bin/activate
python manage.py createsuperuser
```

## 🔧 주요 기능

- **게임 규칙 설명**: GPT 및 Fine-tuning 모델 기반
- **게임 추천**: 사용자 취향 분석
- **QA 데이터 관리**: Django Admin 인터페이스
- **모바일 최적화**: 반응형 웹 디자인

## 📁 프로젝트 구조

```
boardgame_chatbot/
├── boardgame_chatbot/    # 프로젝트 설정
├── chatbot/              # 메인 앱
├── templates/            # HTML 템플릿
├── static/               # 정적 파일
├── deploy_ec2.sh         # EC2 배포 스크립트
└── requirements.txt      # Python 의존성
```

## 🌐 배포 정보

- **프레임워크**: Django 4.2.7
- **데이터베이스**: SQLite (로컬), PostgreSQL (EC2)
- **웹서버**: Nginx + Gunicorn
- **배포**: AWS EC2 Ubuntu

## 🔑 API 키 설정

OpenAI API 키는 `boardgame_chatbot/settings.py`에서 수정:
```python
OPENAI_API_KEY = 'sk-your-actual-api-key-here'
```

## 📞 지원

문제가 있으면 로그를 확인하세요:
```bash
# 애플리케이션 로그
sudo journalctl -u boardgame_chatbot -f

# Nginx 로그  
sudo tail -f /var/log/nginx/error.log
```
