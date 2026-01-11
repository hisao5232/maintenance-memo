#!/bin/bash

# 設定
BACKUP_DIR=$HOME/maintenance/backups
GDRIVE_DIR="gdrive:MaintenanceBackup"
DATE=$(date +%Y%m%d)
FILE_NAME="db_backup_$DATE.sql"

# フォルダ作成
mkdir -p $BACKUP_DIR

# 1. データベースをダンプ (PostgreSQLコンテナから抽出)
docker exec -t maintenance-db pg_dumpall -c -U user > $BACKUP_DIR/$FILE_NAME

# 2. Google Driveへコピー
rclone copy $BACKUP_DIR/$FILE_NAME $GDRIVE_DIR

# 3. サーバー内の古いファイルを削除（7日より前）
find $BACKUP_DIR -type f -mtime +7 -exec rm {} \;

# 4. Google Drive内の古いファイルを削除（30日より前）
rclone delete $GDRIVE_DIR --min-age 30d
