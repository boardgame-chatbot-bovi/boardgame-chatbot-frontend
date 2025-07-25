#!/bin/bash

# =============================================================================
# BOVI 보드게임 채팅봇 완전 자동 EC2 배포 스크립트
# Git pull 후 바로 실행 가능 (어떤 IP든 자동 작동)
# =============================================================================

set -e  # 에러 발생시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "🚀 BOVI 보드게임 채팅봇 완전 자동 배포 시작..."

# 프로젝트 설정
PROJECT_NAME="boardgame_chatbot"
PROJECT_DIR="/home/ubuntu/$PROJECT_NAME"
DB_NAME="boardgame_db"
DB_USER="juno"
DB_PASSWORD="hwang0719"

# 현재 IP 자동 감지
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "unknown")
log_info "감지된 퍼블릭 IP: $PUBLIC_IP"

# 1. 시스템 업데이트
log_info "📦 시스템 패키지 업데이트..."
sudo apt update && sudo apt upgrade -y

# 2. 필수 패키지 설치
log_info "🔧 필수 패키지 설치..."
sudo apt install -y \
    python3 python3-pip python3-venv \
    postgresql postgresql-contrib \
    nginx git curl vim htop

# 3. PostgreSQL 설정 (완전한 권한으로)
log_info "🗄️ PostgreSQL 데이터베이스 설정..."

# 기존 데이터베이스와 사용자 삭제 (에러 무시)
sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null || true
sudo -u postgres psql -c "DROP USER IF EXISTS $DB_USER;" 2>/dev/null || true

# SUPERUSER 권한으로 사용자 생성 (모든 권한)
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD' CREATEDB SUPERUSER;"

# 데이터베이스 생성 (소유자를 해당 사용자로 설정)
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# public 스키마 권한 설정
sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
sudo -u postgres psql -d $DB_NAME -c "GRANT CREATE ON SCHEMA public TO $DB_USER;"
sudo -u postgres psql -d $DB_NAME -c "ALTER SCHEMA public OWNER TO $DB_USER;"

# 기본 설정
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'UTC';"

log_success "PostgreSQL 설정 완료 (SUPERUSER 권한)"

# 4. 프로젝트 디렉토리 이동 (이미 git clone된 상태라고 가정)
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "프로젝트 디렉토리가 없습니다: $PROJECT_DIR"
    log_info "다음 명령어로 프로젝트를 먼저 클론하세요:"
    log_info "git clone https://github.com/yourusername/boardgame_chatbot.git"
    exit 1
fi

cd "$PROJECT_DIR"
log_info "프로젝트 디렉토리: $PROJECT_DIR"

# 5. 파일 권한 설정
sudo chown -R ubuntu:ubuntu "$PROJECT_DIR"

# 6. Python 가상환경 설정
log_info "🐍 Python 가상환경 설정..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-ec2.txt

# 7. static 디렉토리 생성 (경고 해결)
log_info "📁 디렉토리 설정..."
mkdir -p "$PROJECT_DIR/static"
mkdir -p "$PROJECT_DIR/media"

# 8. Django 설정
log_info "🔧 Django 프로젝트 설정..."
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

log_success "Django 설정 완료"

# 9. 소켓 디렉토리 생성
log_info "📁 Gunicorn 소켓 디렉토리 생성..."
sudo mkdir -p /run/gunicorn
sudo chown ubuntu:www-data /run/gunicorn
sudo chmod 755 /run/gunicorn

# 10. Systemd 서비스 설정
log_info "🚀 Gunicorn 서비스 설정..."
sudo tee /etc/systemd/system/boardgame_chatbot.service > /dev/null << EOF
[Unit]
Description=BOVI Boardgame Chatbot Gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn \\
    --access-logfile - \\
    --error-logfile - \\
    --workers 3 \\
    --bind unix:/run/gunicorn/boardgame_chatbot.sock \\
    --timeout 120 \\
    boardgame_chatbot.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# 11. 개선된 Nginx 설정 (Static Files 경로 최적화)
log_info "🌐 Nginx 웹서버 설정 (Static Files 경로 최적화)..."
sudo tee /etc/nginx/sites-available/boardgame_chatbot > /dev/null << EOF
server {
    listen 80;
    server_name _;

    client_max_body_size 100M;

    # 로그 설정
    access_log /var/log/nginx/boardgame_chatbot_access.log;
    error_log /var/log/nginx/boardgame_chatbot_error.log;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    # Static Files 경로 (우선순위: staticfiles > static)
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Access-Control-Allow-Origin "*";
        
        # 파일이 staticfiles에 없으면 static에서 찾기
        try_files \$uri @static_fallback;
    }
    
    # Static Files 대체 경로
    location @static_fallback {
        alias $PROJECT_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Access-Control-Allow-Origin "*";
    }

    # Media Files
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Access-Control-Allow-Origin "*";
    }

    # Django 애플리케이션
    location / {
        proxy_pass http://unix:/run/gunicorn/boardgame_chatbot.sock;
        proxy_set_header Host \$http_host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# 12. Nginx 사이트 활성화 및 파일 복사 (이중 보장)
sudo ln -sf /etc/nginx/sites-available/boardgame_chatbot /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 프로젝트의 nginx 설정 파일도 올바른 위치에 복사 (백업용)
if [ -f "nginx_boardgame_chatbot" ]; then
    sudo cp nginx_boardgame_chatbot /etc/nginx/sites-available/boardgame_chatbot
    sudo ln -sf /etc/nginx/sites-available/boardgame_chatbot /etc/nginx/sites-enabled/
    log_info "프로젝트의 Nginx 설정 파일도 적용했습니다"
fi

# 13. 설정 테스트 및 서비스 시작
log_info "🔄 서비스 시작..."
sudo nginx -t
sudo systemctl daemon-reload
sudo systemctl start boardgame_chatbot
sudo systemctl enable boardgame_chatbot
sudo systemctl restart nginx
sudo systemctl enable nginx

# 14. 방화벽 설정
log_info "🔒 방화벽 설정..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
echo "y" | sudo ufw enable

# 15. Static Files 경로 디버깅 정보 출력
log_info "🔍 Static Files 디버깅 정보..."
echo "=== Static Files 디렉토리 구조 ==="
ls -la "$PROJECT_DIR/static/" 2>/dev/null || echo "static 디렉토리 없음"
ls -la "$PROJECT_DIR/static/chatbot/" 2>/dev/null || echo "static/chatbot 디렉토리 없음"
ls -la "$PROJECT_DIR/staticfiles/" 2>/dev/null || echo "staticfiles 디렉토리 없음"
ls -la "$PROJECT_DIR/staticfiles/chatbot/" 2>/dev/null || echo "staticfiles/chatbot 디렉토리 없음"
echo "================================="

# 16. 서비스 상태 확인
log_info "🔍 서비스 상태 확인..."
sleep 3

GUNICORN_STATUS=$(sudo systemctl is-active boardgame_chatbot)
NGINX_STATUS=$(sudo systemctl is-active nginx)

if [ "$GUNICORN_STATUS" = "active" ]; then
    log_success "✅ Gunicorn 서비스: 실행 중"
else
    log_error "❌ Gunicorn 서비스: $GUNICORN_STATUS"
    sudo journalctl -u boardgame_chatbot --no-pager -n 10
fi

if [ "$NGINX_STATUS" = "active" ]; then
    log_success "✅ Nginx 서비스: 실행 중"
else
    log_error "❌ Nginx 서비스: $NGINX_STATUS"
    sudo tail -n 10 /var/log/nginx/error.log
fi

# 17. 소켓 파일 확인
if [ -S /run/gunicorn/boardgame_chatbot.sock ]; then
    log_success "✅ 소켓 파일 생성됨: /run/gunicorn/boardgame_chatbot.sock"
else
    log_warning "⚠️ 소켓 파일 없음 - 서비스 재시작 중..."
    sudo systemctl restart boardgame_chatbot
    sleep 2
fi

# 18. Static Files 접근 테스트
log_info "🖼️ Static Files 접근 테스트..."
LOGO_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/static/chatbot/logo.png || echo "000")
if [ "$LOGO_STATUS" = "200" ]; then
    log_success "✅ Logo 이미지 접근 가능"
else
    log_warning "⚠️ Logo 이미지 접근 실패 (HTTP $LOGO_STATUS)"
    
    # 수동으로 파일 확인 및 복사
    if [ ! -f "$PROJECT_DIR/staticfiles/chatbot/logo.png" ]; then
        log_info "🔧 Logo 파일 수동 복사 시도..."
        mkdir -p "$PROJECT_DIR/staticfiles/chatbot"
        if [ -f "$PROJECT_DIR/static/chatbot/logo.png" ]; then
            cp "$PROJECT_DIR/static/chatbot/logo.png" "$PROJECT_DIR/staticfiles/chatbot/"
            sudo chown ubuntu:www-data "$PROJECT_DIR/staticfiles/chatbot/logo.png"
            sudo chmod 644 "$PROJECT_DIR/staticfiles/chatbot/logo.png"
            log_info "✅ Logo 파일 복사 완료"
        fi
    fi
fi

# 19. 최종 웹사이트 접근 테스트
log_info "🌐 웹사이트 접근 테스트..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ || echo "000")

if [ "$HTTP_STATUS" = "200" ]; then
    log_success "✅ 웹사이트 정상 접근 가능"
else
    log_warning "⚠️ 웹사이트 접근 상태: $HTTP_STATUS"
    log_info "서비스 재시작 중..."
    sudo systemctl restart boardgame_chatbot
    sudo systemctl reload nginx
    sleep 3
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ || echo "000")
    if [ "$HTTP_STATUS" = "200" ]; then
        log_success "✅ 웹사이트 정상 접근 가능 (재시도 성공)"
    fi
fi

# 20. 배포 완료 메시지
echo ""
echo "============================================================================="
log_success "🎉 BOVI 보드게임 채팅봇 배포 완료! (Static Files 문제 해결)"
echo "============================================================================="
echo ""
log_info "📡 웹사이트: http://$PUBLIC_IP"
log_info "🔧 관리자: http://$PUBLIC_IP/admin"
log_info "🖼️ 로고 이미지: http://$PUBLIC_IP/static/chatbot/logo.png"
echo ""
log_warning "📝 추가 설정이 필요한 경우:"
echo "1. Django 관리자 계정 생성:"
echo "   cd $PROJECT_DIR && source venv/bin/activate"
echo "   python manage.py createsuperuser"
echo ""
echo "2. OpenAI API 키 설정 (settings.py에서):"
echo "   OPENAI_API_KEY = 'sk-your-actual-key-here'"
echo ""
echo "3. Static Files 재수집 (이미지가 안 보이는 경우):"
echo "   cd $PROJECT_DIR && source venv/bin/activate"
echo "   python manage.py collectstatic --noinput --clear"
echo ""
log_info "🔧 유용한 명령어:"
echo "  - 서비스 재시작: sudo systemctl restart boardgame_chatbot"
echo "  - 로그 확인: sudo journalctl -u boardgame_chatbot -f"
echo "  - Nginx 재시작: sudo systemctl restart nginx"
echo "  - Static Files 재수집: cd $PROJECT_DIR && python manage.py collectstatic"
echo ""
echo "============================================================================="

# 배포 정보 저장
cat > /home/ubuntu/deployment_info.txt << EOF
BOVI 보드게임 채팅봇 배포 정보 (Static Files 문제 해결)
=======================================================
배포 일시: $(date)
프로젝트 경로: $PROJECT_DIR
데이터베이스: $DB_NAME
DB 사용자: $DB_USER (SUPERUSER)
DB 비밀번호: $DB_PASSWORD
퍼블릭 IP: $PUBLIC_IP
웹사이트: http://$PUBLIC_IP
관리자: http://$PUBLIC_IP/admin
로고 이미지: http://$PUBLIC_IP/static/chatbot/logo.png

서비스 상태:
- Gunicorn: $GUNICORN_STATUS
- Nginx: $NGINX_STATUS
- HTTP 응답: $HTTP_STATUS
- Logo 이미지: $LOGO_STATUS

Static Files 경로:
- Source: $PROJECT_DIR/static/
- Collected: $PROJECT_DIR/staticfiles/
- Nginx: /static/ -> $PROJECT_DIR/staticfiles/

문제 해결 명령어:
1. Static Files 재수집:
   cd $PROJECT_DIR && source venv/bin/activate && python manage.py collectstatic --noinput --clear

2. 서비스 재시작:
   sudo systemctl restart boardgame_chatbot && sudo systemctl reload nginx

3. 권한 수정:
   sudo chown -R ubuntu:www-data $PROJECT_DIR/staticfiles && sudo chmod -R 755 $PROJECT_DIR/staticfiles
EOF

log_success "배포 정보가 /home/ubuntu/deployment_info.txt에 저장되었습니다."

# 최종 Static Files 확인
echo ""
log_info "🔍 최종 Static Files 확인:"
echo "Logo 파일 존재 여부:"
ls -la "$PROJECT_DIR/static/chatbot/logo.png" 2>/dev/null && echo "✅ Source 파일 존재" || echo "❌ Source 파일 없음"
ls -la "$PROJECT_DIR/staticfiles/chatbot/logo.png" 2>/dev/null && echo "✅ Collected 파일 존재" || echo "❌ Collected 파일 없음"
