#!/bin/bash

# =============================================================================
# BOVI 보드게임 채팅봇 - 코드 업데이트 스크립트
# Git pull 후 서비스 재시작
# =============================================================================

set -e

echo "🔄 BOVI 보드게임 채팅봇 업데이트 시작..."

PROJECT_DIR="/home/ubuntu/boardgame_chatbot"

# 프로젝트 디렉토리로 이동
cd "$PROJECT_DIR"

# Git에서 최신 코드 받기
echo "📥 최신 코드 다운로드 중..."
git pull origin main

# 가상환경 활성화
source venv/bin/activate

# 의존성 업데이트
echo "📦 Python 패키지 업데이트 중..."
pip install -r requirements.txt

# Django 설정
echo "🔧 Django 설정 업데이트 중..."
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

# 서비스 재시작
echo "🔄 서비스 재시작 중..."
sudo systemctl restart boardgame_chatbot
sudo systemctl reload nginx

# 상태 확인
echo "✅ 업데이트 완료!"
echo "서비스 상태:"
sudo systemctl status boardgame_chatbot --no-pager -l
echo ""
echo "웹사이트: http://13.125.251.186"
