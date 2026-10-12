# tiritara.dev

tiritara.dev の開発者サイト（GitHub Pages）。アプリ・Web サービスの一覧と、それぞれの詳細ページを静的 HTML で公開しています。

## 構成

- `index.html` — トップページ（アプリ / Web サービス / ツール）
- `apps/<slug>/` — アプリ詳細ページ（Google Play・App Store へのリンク付き）
- `web/<slug>/` — Web サービス詳細ページ
- `data/projects.json` — 掲載するアプリ・Web サービス・ツールの一覧（手で編集する）
- `data/store.json` — ストアから取得した説明文・バージョンなど（自動生成）
- `assets/apps/<slug>/` — ストアから取得したアイコンとスクリーンショット（自動生成）
- `assets/site.css` — 全ページ共通のスタイル

`index.html`・`apps/`・`web/`・`sitemap.xml` は生成物です。直接編集せず、下の手順で作り直してください。

## 更新手順

アプリを追加するときは `data/projects.json` の `apps` に項目を足します（`play` は Android のパッケージ名、`ios` は App Store の ID。片方だけでも可）。

```bash
python3 tools/fetch_store_data.py   # ストアの説明文・画像を取り直す
python3 tools/build.py              # ページを生成する
```

文言やデザインだけを変えたときは `tools/build.py` だけで構いません。Python 3 の標準ライブラリだけで動きます。
