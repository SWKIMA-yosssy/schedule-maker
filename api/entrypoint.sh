#!/bin/sh

# このスクリプトは、DBが準備完了になるまで待機します。
# データベースのホスト名（db）とポート（5432）はご自身の環境に合わせてください。

# Pythonを使ってTCP接続を試みる小さなループ
until python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.connect(('db', 5432))"; do
  echo "Waiting for database..."
  sleep 1
done

echo "Database is up - running migrations..."
python -m app.migrate_db

echo "Starting web server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
