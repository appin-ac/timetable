# 新しいホームページ

自動化・省力化を重視しながら作っているホームページ。

現在のコンテンツはブログと宮崎県内の主要駅の時刻表。

## サイトの生成

Python 3 が必要です。初回のみ、必要なライブラリをインストールします。

```powershell
python -m pip install Markdown Jinja2
```

次に、リポジトリの `src` ディレクトリへ移動して生成スクリプトを実行します。

```powershell
cd src
python generate.py
```

`generate.py` は `data` の時刻表データと `articles` のブログ記事を読み込み、生成したHTMLを `docs` に出力します。パスは実行時のカレントディレクトリを基準にしているため、必ず `src` から実行してください。

生成後は `docs/index.html` をブラウザーで開くと、サイトを確認できます。

## データの追加・更新

### 時刻表

駅ごとのフォルダーを `data` に置き、年ごとのCSVと同じ年のJSONを用意します。

```text
data/
└── 駅を表すフォルダー/
    ├── 2026.csv
    └── 2026.json
```

CSVには時刻表の行データ、JSONには路線名・駅名・方向・改正日などの情報を記述します。既存ファイルの列名やJSONの項目に合わせてください。データを追加したら、上記の手順でサイトを再生成します。

### ブログ記事

`articles` にMarkdownファイル（`.md`）を追加します。ファイルの先頭に `title` と `date` を記述したフロントマターが必要です。

```markdown
---
title: 記事のタイトル
date: 2026-10-25
---

記事本文をMarkdownで記述します。
```

日付は `YYYY-MM-DD` 形式で指定します。記事ページは `docs/blog` に生成され、トップページの記事一覧は日付の新しい順に更新されます。

## ディレクトリ構成

```text
articles/   ブログ記事のMarkdown原稿
data/       駅・年ごとのCSVおよびJSONデータ
docs/       生成されたサイト（HTML、CSS、画像、JavaScript）
src/        HTMLテンプレートと生成スクリプト
```
