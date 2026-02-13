#!/bin/bash
set -e

printenv | grep -E '^(INP_|NTFY_)' > /app/.env

CRON_SCHEDULE="${CRON_SCHEDULE:-*/15 * * * *}"

echo "📅 Configuration cron: $CRON_SCHEDULE"

echo "$CRON_SCHEDULE cd /app && /usr/local/bin/python main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/pegase-cron
chmod 0644 /etc/cron.d/pegase-cron
crontab /etc/cron.d/pegase-cron

touch /var/log/cron.log

echo "🚀 Exécution initiale..."
cd /app && python main.py

echo "⏰ Démarrage du scheduler cron..."
cron && tail -f /var/log/cron.log
