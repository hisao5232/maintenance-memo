# 🛠️ 建設機械整備メモ & マニュアル管理アプリ

建設機械の修理エンジニアとしての知見を蓄積するための、自己専用のWebアプリケーションです。
FastAPI（バックエンド）とStreamlit（フロントエンド）を組み合わせ、エックスサーバーVPS上のDocker環境で稼働しています。

## 🏗️ システム構成
- **Frontend**: Streamlit (Python)
- **Backend**: FastAPI (Python / Pydantic)
- **Database**: PostgreSQL 15
- **Infrastructure**: Ubuntu 24.04 (VPS) / Docker Compose
- **Reverse Proxy**: Traefik (HTTPS / Let's Encrypt)

## 📁 ディレクトリ構成
```text
.
├── backend/          # FastAPI APIサーバー
├── frontend/         # Streamlit ユーザーインターフェース
├── docker-compose.yml # コンテナオーケストレーション
└── .env               # 環境変数（Git非公開）

## 🚀 起動方法
.env.example をコピーして .env を作成し、必要な情報を入力します。

以下のコマンドを実行します。

```Bash
docker compose up -d --build
```

## 👨‍💻 開発者
- Hisao (Repair Engineer / Python Learner)

- GitHub: hisao5232