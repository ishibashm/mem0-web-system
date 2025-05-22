# Mem0 ウェブシステム

mem0を使用したクロスプラットフォーム生成AIメモリウェブシステム

## 機能

- ユーザー認証（パスワード認証とOAuth 2.0）
  - Google、GitHub、Apple Sign In対応
- チャットインターフェース
- 高度なメモリ検索機能
  - 時系列ベースの履歴検索
  - キーワード検索（全文検索）
  - トピック（会話単位）による分類
  - ベクトル検索（埋め込みを用いた意味検索）
- ユーザーごとのメモリスコープ切替
- ユーザー設定可能なメモリオプション
  - メモリ保持期間
  - トピックごとの最大メモリ数
  - デフォルト検索タイプ
  - デフォルトスコープ
  - 埋め込みモデル
  - 言語設定
- ネイティブアプリとの連携API（Android優先）
- 複数のLLMプロバイダー対応（OpenAI, Anthropic, Cohere, Groq）
- 日本語サポート

## 技術スタック

### フロントエンド
- Next.js
- React
- Tailwind CSS
- Vercel AI SDK
- mem0ai JavaScript SDK

### バックエンド
- FastAPI
- SQLite（ユーザーデータ用）
- mem0ai Python SDK
- JWT認証
- OAuth 2.0（Google、GitHub、Apple）

### モバイル連携
- Android優先のAPIクライアント
- OkHttp（Androidネットワーク通信）
- Kotlin Coroutines

## 始め方

### 前提条件
- Node.js 18+
- Python 3.9+
- mem0 APIキー
- LLMプロバイダーAPIキー（OpenAI, Anthropic, Cohere, Groq）
- OAuth用のクライアントID/シークレット（Google, GitHub, Apple）

### バックエンドのセットアップ
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### フロントエンドのセットアップ
```bash
cd frontend
npm install
npm run dev
```

## 使い方

1. アカウントを登録（パスワード認証またはOAuth）
2. 設定画面でAPIキーを設定
3. ユーザー設定で好みのオプションを設定
4. チャットを開始
5. メモリの検索や管理

## ネイティブアプリ連携

ネイティブアプリは以下のAPIエンドポイントを使用して連携できます：

- `/api/v1/search` - メモリ検索
- `/api/v1/chat` - チャット機能
- `/api/v1/user/profile` - ユーザープロファイル取得

詳細なAPI仕様については、バックエンドの実行後に `/docs` エンドポイントにアクセスしてください。

Android連携サンプルについては、`android`ディレクトリを参照してください。

## ライセンス

MIT
