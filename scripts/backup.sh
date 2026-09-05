#!/usr/bin/env bash
# hex-auth MySQL 数据库备份脚本
#
# 用法:
#   ./backup.sh [备份目录] [保留天数]
#   默认备份到 ./backups，保留 14 天
#
# 数据库连接信息优先从 backend/.env 的 DATABASE_URL 读取。
# 建议 crontab 定时执行，例如每天凌晨3点：
#   0 3 * * * /path/to/hex-auth/scripts/backup.sh /var/backups/hex-auth 14 >> /var/log/hex-auth-backup.log 2>&1
set -euo pipefail

BACKUP_DIR="${1:-./backups}"
RETENTION_DAYS="${2:-14}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../backend/.env"

if [ -f "$ENV_FILE" ]; then
  DB_URL=$(grep -E '^DATABASE_URL=' "$ENV_FILE" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
elif [ -n "${DATABASE_URL:-}" ]; then
  DB_URL="$DATABASE_URL"
else
  echo "错误: 未找到 backend/.env 且未设置 DATABASE_URL 环境变量" >&2
  exit 1
fi

# 解析 mysql+pymysql://user:pass@host:port/dbname?params
REGEX='mysql\+pymysql://([^:]+):([^@]+)@([^:/]+):?([0-9]*)/(.+)'
if ! [[ $DB_URL =~ $REGEX ]]; then
  echo "错误: 无法解析 DATABASE_URL" >&2
  exit 1
fi
DB_USER="${BASH_REMATCH[1]}"
DB_PASS="${BASH_REMATCH[2]}"
DB_HOST="${BASH_REMATCH[3]}"
DB_PORT="${BASH_REMATCH[4]:-3306}"
DB_NAME="${BASH_REMATCH[5]%%\?*}"   # 去掉 ?charset=... 等参数

mkdir -p "$BACKUP_DIR"
STAMP=$(date +%F_%H%M%S)
FILE="$BACKUP_DIR/${DB_NAME}_${STAMP}.sql"

mysqldump -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" \
  --single-transaction --triggers --routines --no-tablespaces \
  "$DB_NAME" > "$FILE"
gzip -f "$FILE"

# 清理超过保留期的旧备份
find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -type f -mtime +"$RETENTION_DAYS" -delete

echo "备份完成: ${FILE}.gz"
