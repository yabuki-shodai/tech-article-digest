# tech-article-digest

GitHub Issue に Qiita または Zenn の記事 URL を貼り、`summarize` ラベルを付けると、Gemini が日本語で要約して Issue に投稿します。成功時は `completed` ラベルを付けて Issue を閉じ、失敗時は `failed` ラベルを付けて Issue を開いたままにします。

## セットアップ

1. Repository Settings の Actions secrets に `GEMINI_API_KEY` を登録する。
2. 必要なら Actions variables に `GEMINI_MODEL` を登録する。未設定時は `gemini-2.5-flash` を使う。
3. リポジトリに `summarize` ラベルを作成する。
4. Qiita または Zenn の記事 URL を本文に含む Issue を作り、`summarize` ラベルを付ける。

`completed` と `failed` ラベルは、初回利用時にワークフローが存在しなければ作成します。

## 対応 URL

- `https://qiita.com/...`
- `https://zenn.dev/...`

Issue 本文で最初に見つかった HTTP(S) URL だけを処理します。HTTPS、許可ドメイン、標準ポート以外は拒否します。

## ローカル実行

GitHub の `issues.labeled` イベント JSON を用意し、次の環境変数を設定します。

```bash
export GITHUB_TOKEN=...
export GITHUB_EVENT_PATH=/path/to/event.json
export GEMINI_API_KEY=...
export GEMINI_MODEL=gemini-2.5-flash  # 任意

python -m pip install .
python -m src.main
```

## 構成

- `src/fetchers`: サイト固有の記事取得
- `src/ai`: Gemini API クライアント
- `src/github`: GitHub API クライアント
- `src/services`: 要約と Issue 処理
- `src/main.py`: 実行フローとエラーハンドリング

新しいサイトは `BaseFetcher` の実装と、`IssueService` の fetcher 登録を追加して対応します。
