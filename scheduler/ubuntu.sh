#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CRON_JOB="0 2 * * * cd $PROJECT_DIR && docker compose run --rm pricetrail python -c 'from scraper.scraper import run; run()' >> logs/scraper.log 2>&1"

(crontab -l 2>/dev/null | grep -v "docker compose run --rm pricetrail"; echo "$CRON_JOB") | crontab -

echo "Cron job instalado:"
echo "$CRON_JOB"