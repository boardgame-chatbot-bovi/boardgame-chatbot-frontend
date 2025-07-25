# 🎲 BOVI 보드게임 채팅봇 - 완벽한 원클릭 배포

## ⚡ AWS EC2 배포 (완전 자동화)

### 📋 사전 준비
1. **EC2 인스턴스 생성**
   - AMI: Ubuntu Server 22.04 LTS
   - 인스턴스 타입: t2.micro 이상
   - 보안 그룹: HTTP(80), SSH(22) 열기

2. **EC2 접속**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

### 🚀 원클릭 배포

```bash
# 1. 프로젝트 클론
cd /home/ubuntu
rm -rf boardgame_chatbot  # 기존 것이 있다면 삭제
git clone https://github.com/yourusername/boardgame_chatbot.git
cd boardgame_chatbot

# 2. 자동 배포 실행
chmod +x deploy_ec2.sh
./deploy_ec2.sh

# 3. 관리자 계정 생성
source venv/bin/activate
python manage.py createsuperuser
```

### ✅ 배포 완료!
- **웹사이트**: http://your-ec2-ip
- **관리자**: http://your-ec2-ip/admin
- **QR 코드**: 웹사이트에서 모바일 접속용 QR 코드 제공

## 🔄 코드 업데이트

```bash
cd /home/ubuntu/boardgame_chatbot
chmod +x update.sh
./update.sh
```

## 🔧 주요 기능

- **자동 환경 감지**: 로컬/EC2 환경 자동 구분
- **데이터베이스**: SQLite(로컬) / PostgreSQL(EC2)
- **웹서버**: Nginx + Gunicorn
- **정적 파일**: WhiteNoise
- **로그**: 실시간 모니터링 가능
- **QR 코드**: 모바일 접속용 QR 코드 자동 생성

## 📱 QR 코드 기능

### 자동 URL 설정
배포 시 QR 코드가 자동으로 EC2 IP를 사용합니다:

```bash
# 자동 설정됨
export QR_BASE_URL=http://your-ec2-ip:8000
```

### IP 변경 시 업데이트

EC2 IP가 변경될 경우:

```bash
cd /home/ubuntu/boardgame_chatbot
chmod +x update_qr_url.sh
./update_qr_url.sh
```

### 수동 URL 설정

특정 도메인을 사용하고 싶은 경우:

```bash
# 환경변수 설정
export QR_BASE_URL=https://your-domain.com
sudo systemctl restart boardgame_chatbot
```

## 📁 프로젝트 구조

```
boardgame_chatbot/
├── boardgame_chatbot/        # Django 설정
├── chatbot/                  # 메인 앱
├── templates/                # HTML 템플릿
├── static/                   # 정적 파일
├── deploy_ec2.sh            # EC2 자동 배포
├── update.sh                # 코드 업데이트
├── update_qr_url.sh         # QR 코드 URL 업데이트
├── fix_postgres.sh          # DB 문제 해결
├── .env.ec2                 # EC2용 환경변수
├── requirements.txt         # 로컬용 패키지
├── requirements-ec2.txt     # EC2용 패키지
└── nginx_boardgame_chatbot  # Nginx 설정
```

## 🛠️ 설정 정보

### 데이터베이스 (EC2)
- **이름**: `boardgame_db`
- **사용자**: `juno`
- **비밀번호**: `hwang0719`

### 환경별 설정
- **로컬**: SQLite, DEBUG=True
- **EC2**: PostgreSQL, 자동 감지

## 🔍 문제 해결

### 로그 확인
```bash
# 애플리케이션 로그
sudo journalctl -u boardgame_chatbot -f

# Nginx 로그
sudo tail -f /var/log/nginx/error.log

# 서비스 상태
sudo systemctl status boardgame_chatbot nginx
```

### 서비스 재시작
```bash
sudo systemctl restart boardgame_chatbot
sudo systemctl reload nginx
```

### PostgreSQL 문제 해결
```bash
chmod +x fix_postgres.sh
./fix_postgres.sh
```

### QR 코드 문제 해결
```bash
# IP 변경 시 QR 코드 업데이트
chmod +x update_qr_url.sh
./update_qr_url.sh

# 수동 URL 설정
export QR_BASE_URL=http://your-new-ip:8000
sudo systemctl restart boardgame_chatbot
```

## 🎯 특징

✅ **완전 자동화**: Git clone → 스크립트 실행만으로 배포 완료  
✅ **환경 감지**: 로컬/EC2 자동 구분  
✅ **QR 코드**: 모바일 접속용 QR 코드 자동 생성  
✅ **에러 친화적**: 자세한 로그와 디버그 정보  
✅ **업데이트 간편**: Git pull → 스크립트 실행  
✅ **민감정보 없음**: 모든 설정이 코드에 포함  

## 🚀 개발자 정보

**프로젝트**: BOVI 보드게임 채팅봇  
**개발자**: juno  
**배포**: AWS EC2 Ubuntu  
**프레임워크**: Django 4.2.7  
