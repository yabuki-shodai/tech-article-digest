# tech-article-digest

GitHub Issue に Qiita または Zenn の記事 URL を登録すると、Gemini が背景、詳細解説、実践方法、注意点、用語集を含む日本語の詳細ダイジェストを Issue に投稿します。成功時は `completed` ラベルを付けて Issue を閉じ、失敗時は `failed` ラベルを付けて Issue を開いたままにします。

## セットアップ

1. Repository Settings の Actions secrets に `GEMINI_API_KEY` を登録する。
2. 必要なら Actions variables に `GEMINI_MODEL` を登録する。未設定時は `gemini-3.5-flash` を使う。
3. `Issues` → `New issue` → `記事を要約する`を選ぶ。
4. QiitaまたはZennの記事URLだけを入力してIssueを作成する。

Issue作成時の仮タイトルは自動入力されます。記事取得後、Issueタイトルを実際の記事タイトルへ自動変更します。`summarize`、`completed`、`failed`ラベルも必要に応じて自動作成します。

失敗したIssueを再実行する場合は、原因を修正してから`summarize`ラベルを付けます。

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
export GEMINI_MODEL=gemini-3.5-flash  # 任意

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
