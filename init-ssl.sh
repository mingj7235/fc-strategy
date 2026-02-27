#!/bin/bash
# SSL 초기 설정 스크립트 (최초 1회만 실행)
# 사용법: bash init-ssl.sh

set -e

DOMAIN="fc-strategy.org"
EMAIL="joshuara7235@gmail.com"
COMPOSE="docker compose --env-file .env.prod -f docker-compose.prod.yml"

echo "=== Step 1: 기존 볼륨 정리 ==="
$COMPOSE down
docker volume rm -f fc-strategy_certbot_conf fc-strategy_certbot_www 2>/dev/null || true

echo "=== Step 2: 임시 자체서명 인증서 생성 ==="
docker volume create fc-strategy_certbot_conf
docker volume create fc-strategy_certbot_www

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

echo "=== Step 3: Nginx 시작 (임시 인증서) ==="
$COMPOSE up -d frontend
echo "Nginx 안정화 대기 (5초)..."
sleep 5

echo "=== Step 4: 임시 인증서 삭제 ==="
docker run --rm \
  -v fc-strategy_certbot_conf:/etc/letsencrypt \
  alpine sh -c "rm -rf /etc/letsencrypt/live/$DOMAIN /etc/letsencrypt/renewal/$DOMAIN.conf /etc/letsencrypt/archive/$DOMAIN"

echo "=== Step 5: Let's Encrypt 인증서 발급 ==="
docker run --rm \
  -v fc-strategy_certbot_www:/var/www/certbot \
  -v fc-strategy_certbot_conf:/etc/letsencrypt \
  certbot/certbot certonly \
    --webroot -w /var/www/certbot \
    -d $DOMAIN -d www.$DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email

echo "=== Step 6: 전체 서비스 재시작 (진짜 인증서) ==="
$COMPOSE down
$COMPOSE up -d

echo ""
echo "=== 완료! ==="
echo "https://$DOMAIN 으로 접속해보세요!"
