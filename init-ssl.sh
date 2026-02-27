#!/bin/bash
# SSL 초기 설정 스크립트 (최초 1회만 실행)
# 사용법: bash init-ssl.sh

set -e

DOMAIN="fc-strategy.org"
EMAIL="joshuara7235@gmail.com"
COMPOSE="docker compose --env-file .env.prod -f docker-compose.prod.yml"

echo "=== Step 1: 임시 자체서명 인증서 생성 ==="
$COMPOSE down

# certbot_conf 볼륨에 임시 인증서 생성
docker run --rm \
  -v fc-strategy_certbot_conf:/etc/letsencrypt \
  alpine sh -c "
    mkdir -p /etc/letsencrypt/live/$DOMAIN &&
    apk add --no-cache openssl &&
    openssl req -x509 -nodes -days 1 -newkey rsa:2048 \
      -keyout /etc/letsencrypt/live/$DOMAIN/privkey.pem \
      -out /etc/letsencrypt/live/$DOMAIN/fullchain.pem \
      -subj '/CN=$DOMAIN'
  "

echo "=== Step 2: Nginx 시작 (임시 인증서) ==="
$COMPOSE up -d frontend

echo "=== Step 3: Let's Encrypt 인증서 발급 ==="
# 임시 인증서 삭제 후 진짜 인증서 발급
docker run --rm \
  -v fc-strategy_certbot_www:/var/www/certbot \
  -v fc-strategy_certbot_conf:/etc/letsencrypt \
  certbot/certbot certonly \
    --webroot -w /var/www/certbot \
    -d $DOMAIN -d www.$DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --force-renewal

echo "=== Step 4: 전체 서비스 재시작 (진짜 인증서) ==="
$COMPOSE down
$COMPOSE up -d

echo ""
echo "=== 완료! ==="
echo "https://$DOMAIN 으로 접속해보세요!"
