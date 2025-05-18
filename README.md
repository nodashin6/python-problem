<div align="center">

> [!NOTE]
> **開発中です！** 本パッケージは現在PoCフェーズです。



# 🐍 Python Problem

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15.3+-black?logo=next.js&logoColor=white)](https://nextjs.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**雰囲気でつくるPythonプログラミング学習プラットフォーム** ✨<br>
コーディング、提出、即時フィードバック。プログラミング力を手軽に強化。

<p align="center">
  <a href="#-特徴">特徴</a> •
  <a href="#-使い方">使い方</a> •
  <a href="#%EF%B8%8F-開発環境構築">開発環境構築</a> •
  <a href="#-システム構成">システム構成</a> •
  <a href="#-ライセンス">ライセンス</a>
</p>

</div>

## ✨ 特徴

プログラミングの基礎から応用まで、実践的なスキルを育てるプラットフォーム

- 🚀 **多様な問題セット** — 初心者から上級者まで幅広いレベルの問題
- 🔍 **リアルタイム評価** — 自動採点システム（AC/WA/CE/RE/TLE）
- 📊 **進捗トラッキング** — 解答履歴と成長の可視化
- 📝 **豊かな問題表現** — 数式対応のマークダウンで複雑な問題も明確に
- 🌐 **モダンUI** — ストレスのない直感的な操作感

## 🚀 使い方

1. フロントエンドとバックエンドを起動
2. ブラウザで `http://localhost:3000` にアクセス
3. 問題リストから挑戦したい問題を選択
4. コードを書いて提出
5. 即座にフィードバックを受け取り、改善

## ⚙️ 開発環境構築

### フロントエンド (Next.js)

```bash
# Node.js環境をセットアップ (Volta推奨)
curl https://get.volta.sh | bash
source ~/.bashrc  # または新しいターミナルを開く

# Node.jsとnpmをインストール
volta install node@22
volta install npm

# フロントエンドをセットアップ
cd frontend
npm install
npm run dev  # 開発サーバー起動 (http://localhost:3000)
```

### バックエンド (FastAPI)

```bash
# Poetryをインストール
curl -sSL https://install.python-poetry.org | python3 -

# バックエンドをセットアップ
cd judge-system
poetry install
poetry run uvicorn src.main:app --reload  # APIサーバー起動 (http://localhost:8000)
```

## 🔧 システム構成

| コンポーネント | 技術スタック | 説明 |
|------------|------------|------|
| **フロントエンド** | Next.js, React, TypeScript | モダンで高速なSPA体験を提供 |
| **バックエンド** | FastAPI, Python | 高性能な非同期APIフレームワーク |
| **依存管理** | Poetry, npm | 効率的なパッケージ管理 |

## 📚 問題セット

現在提供している問題カテゴリ:
- 🔰 **getting-started** — プログラミングの基礎を学ぶ

## 🧪 システム要件

- Python 3.12以上
- Node.js 22以上
- Poetry 1.5以上

## 📋 将来の拡張予定

- [ ] 追加の問題セット
- [ ] ユーザー認証システム
- [ ] グローバルリーダーボード
- [ ] コード実行の詳細メトリクス

## 📜 ライセンス

このプロジェクトは [LICENSE](LICENSE) ファイルに記載されたライセンスの下で公開されています。

---

<div align="center">
Made with ❤️ by <a href="https://github.com/nodashin">nodashin</a>
</div>

