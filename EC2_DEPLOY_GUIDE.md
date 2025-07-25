# 🚀 BOVI EC2 배포 가이드

## 📋 **준비사항**

### 1. AWS EC2 인스턴스 생성
- **AMI**: Ubuntu Server 22.04 LTS
- **인스턴스 타입**: t2.micro (프리티어) 또는 t3.small
- **보안 그룹**: HTTP(80), HTTPS(443), SSH(22) 열기
- **키 페어**: 생성 후 다운로드

### 2. 로컬에서 준비
```bash
# 프로젝트 테스트
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

# Git에 업로드 (또는 scp로 직접 전송)
```

## 🔧 **EC2 서버 설정**

### 1단계: EC2 접속
```bash
# SSH로 EC2 접속
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 2단계: 자동 설정 스크립트 실행
```bash
# 스크립트 다운로드 및 실행
chmod +x deploy_ec2.sh
./deploy_ec2.sh
```

### 3단계: 프로젝트 업로드
```bash
# 방법 1: Git clone
cd /home/ubuntu
git clone https://github.com/your-repo/boardgame_chatbot.git

# 방법 2: SCP로 직접 전송
# 로컬에서 실행:
scp -i your-key.pem -r /path/to/boardgame_chatbot ubuntu@your-ec2-ip:/home/ubuntu/
```

### 4단계: 가상환경 및 의존성 설치
```bash
cd /home/ubuntu/boardgame_chatbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5단계: 환경변수 설정
```bash
# .env 파일 생성
cp .env.example .env
nano .env

# 다음 내용 수정:
DEBUG=False
SECRET_KEY=your-very-secret-key-here
ALLOWED_HOSTS=your-ec2-ip,your-domain.com
DATABASE_URL=postgres://boardgame_user:your_password_here@localhost:5432/boardgame_db
OPENAI_API_KEY=your-openai-api-key-here
```

### 6단계: 데이터베이스 마이그레이션
```bash
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

# 관리자 계정 생성
python manage.py createsuperuser
```

### 7단계: Gunicorn 서비스 설정
```bash
# Gunicorn 서비스 파일 복사
sudo cp boardgame_chatbot.service /etc/systemd/system/

# 서비스 시작
sudo systemctl start boardgame_chatbot
sudo systemctl enable boardgame_chatbot
sudo systemctl status boardgame_chatbot
```

### 8단계: Nginx 설정
```bash
# Nginx 설정 파일 복사
sudo cp nginx_boardgame_chatbot /etc/nginx/sites-available/

# 사이트 활성화
sudo ln -s /etc/nginx/sites-available/nginx_boardgame_chatbot /etc/nginx/sites-enabled

# 기본 설정 제거
sudo rm /etc/nginx/sites-enabled/default

# Nginx 설정 테스트 및 재시작
sudo nginx -t
sudo systemctl restart nginx
```

## 🎯 **QA 데이터베이스 활용**

### Django Admin에서 QA 데이터 관리
```
http://your-ec2-ip/admin/
```

### 테이블 구조:
1. **GPT Rule QAs**
   - ID (자동 증가)
   - 게임 이름
   - 질문
   - 답변

2. **Finetuning Rule QAs**
   - ID (자동 증가)
   - 게임 이름
   - 질문
   - 답변

### 샘플 데이터 추가 (Django Shell)
```bash
python manage.py shell
```

```python
from chatbot.models import GPTRuleQA, FinetuningRuleQA

# GPT 룰 QA 샘플 데이터
GPTRuleQA.objects.create(
    game_name="카탄",
    question="카탄 게임의 기본 룰을 알려주세요",
    answer="카탄은 3-4명이 플레이하는 전략 보드게임입니다..."
)

# 파인튜닝 룰 QA 샘플 데이터
FinetuningRuleQA.objects.create(
    game_name="카탄",
    question="카탄에서 개발 카드 사용 시점은?",
    answer="개발 카드는 구매한 턴에는 사용할 수 없습니다..."
)
```

## 🔍 **트러블슈팅**

### 로그 확인
```bash
# Gunicorn 로그
sudo journalctl -u boardgame_chatbot -f

# Nginx 로그
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 서비스 재시작
```bash
sudo systemctl restart boardgame_chatbot
sudo systemctl restart nginx
```

### 정적 파일 문제
```bash
python manage.py collectstatic --clear --noinput
sudo systemctl restart boardgame_chatbot
```

## 🌐 **도메인 연결 (선택사항)**

### 1. Route 53에서 도메인 설정
### 2. Nginx에서 server_name 수정
### 3. Let's Encrypt SSL 인증서 설정

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## ✅ **배포 완료 체크리스트**

- [ ] EC2 인스턴스 생성 및 보안 그룹 설정
- [ ] PostgreSQL 설치 및 데이터베이스 생성
- [ ] 프로젝트 업로드 및 의존성 설치
- [ ] 환경변수 설정 (.env)
- [ ] 데이터베이스 마이그레이션
- [ ] Gunicorn 서비스 설정
- [ ] Nginx 설정 및 실행
- [ ] 관리자 계정 생성
- [ ] QA 데이터 추가
- [ ] 전체 기능 테스트

**🎉 배포 완료!** 
- 웹사이트: `http://your-ec2-ip`
- 관리자: `http://your-ec2-ip/admin`
