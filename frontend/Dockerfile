FROM python:3.11-slim

WORKDIR /app

# 依存ライブラリのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードのコピー
COPY . .

# Streamlitのデフォルトポート
EXPOSE 8501

# サーバー起動コマンド
# --server.address=0.0.0.0 を指定しないと外部からアクセスできません
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
