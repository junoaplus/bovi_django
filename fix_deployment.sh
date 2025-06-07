#!/bin/bash

# =============================================================================
# 배포 문제 해결 스크립트
# EC2에서 실행: ./fix_deployment.sh
# =============================================================================

set -e

echo "🔧 BOVI 보드게임 채팅봇 배포 문제 해결 중..."

# 1. 현재 상태 확인
echo "📊 현재 서비스 상태:"
sudo systemctl is-active boardgame_chatbot || echo "Gunicorn 서비스 중지됨"
sudo systemctl is-active nginx || echo "Nginx 서비스 중지됨"

# 2. 소켓 디렉토리 생성 및 권한 설정
echo "📁 소켓 디렉토리 설정..."
sudo mkdir -p /run/gunicorn
sudo chown ubuntu:www-data /run/gunicorn
sudo chmod 755 /run/gunicorn

# 3. Nginx 설정 파일 생성 (올바른 IP로)
echo "🌐 Nginx 설정 업데이트..."
sudo tee /etc/nginx/sites-available/boardgame_chatbot > /dev/null << 'EOF'
server {
    listen 80;
    server_name 13.125.251.186 _;

    client_max_body_size 100M;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        alias /home/ubuntu/boardgame_chatbot/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/ubuntu/boardgame_chatbot/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn/boardgame_chatbot.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
EOF

# 4. Systemd 서비스 파일 업데이트
echo "🚀 Gunicorn 서비스 설정 업데이트..."
sudo tee /etc/systemd/system/boardgame_chatbot.service > /dev/null << 'EOF'
[Unit]
Description=BOVI Boardgame Chatbot Gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/boardgame_chatbot
Environment="PATH=/home/ubuntu/boardgame_chatbot/venv/bin"
EnvironmentFile=/home/ubuntu/boardgame_chatbot/.env
ExecStart=/home/ubuntu/boardgame_chatbot/venv/bin/gunicorn \
    --access-logfile - \
    --error-logfile - \
    --workers 3 \
    --bind unix:/run/gunicorn/boardgame_chatbot.sock \
    --timeout 120 \
    boardgame_chatbot.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# 5. Nginx 사이트 활성화
echo "⚙️ Nginx 사이트 활성화..."
sudo ln -sf /etc/nginx/sites-available/boardgame_chatbot /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 6. 설정 파일 테스트
echo "🧪 설정 파일 테스트..."
if sudo nginx -t; then
    echo "✅ Nginx 설정 OK"
else
    echo "❌ Nginx 설정 오류"
    exit 1
fi

# 7. 정적 파일 수집
echo "📦 정적 파일 수집..."
cd /home/ubuntu/boardgame_chatbot
source venv/bin/activate
python manage.py collectstatic --noinput

# 8. 서비스 재시작
echo "🔄 서비스 재시작..."
sudo systemctl daemon-reload
sudo systemctl stop boardgame_chatbot 2>/dev/null || true
sudo systemctl start boardgame_chatbot
sudo systemctl enable boardgame_chatbot
sudo systemctl restart nginx

# 9. 서비스 상태 확인
echo "📊 서비스 상태 확인..."
sleep 3

if sudo systemctl is-active --quiet boardgame_chatbot; then
    echo "✅ Gunicorn 서비스: 실행 중"
else
    echo "❌ Gunicorn 서비스: 오류"
    echo "로그:"
    sudo journalctl -u boardgame_chatbot --no-pager -n 10
fi

if sudo systemctl is-active --quiet nginx; then
    echo "✅ Nginx 서비스: 실행 중"
else
    echo "❌ Nginx 서비스: 오류"
    echo "로그:"
    sudo tail -n 10 /var/log/nginx/error.log
fi

# 10. 소켓 파일 확인
echo "🔍 소켓 파일 확인..."
if [ -S /run/gunicorn/boardgame_chatbot.sock ]; then
    echo "✅ 소켓 파일 존재: /run/gunicorn/boardgame_chatbot.sock"
    ls -la /run/gunicorn/boardgame_chatbot.sock
else
    echo "❌ 소켓 파일 없음"
fi

# 11. 방화벽 확인
echo "🔒 방화벽 상태:"
sudo ufw status

echo ""
echo "============================================================================="
echo "🎉 설정 완료!"
echo "웹사이트: http://13.125.251.186"
echo "============================================================================="
echo ""
echo "문제가 지속되면 다음 명령어로 로그를 확인하세요:"
echo "sudo journalctl -u boardgame_chatbot -f"
echo "sudo tail -f /var/log/nginx/error.log"
