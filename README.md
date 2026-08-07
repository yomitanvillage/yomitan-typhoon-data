# yomitan-typhoon-data

読谷村台風情報ダッシュボードのために、沖縄電力の停電マップAPI（`xml_map_koazaBetsu.php`）を
GitHub Actionsで15分ごとに取得し、`data/yomitan_outage.json` に書き出すリポジトリです。

このAPIはブラウザから直接fetchするとCORSでブロックされますが、GitHub Actions（サーバー側）
からの取得は問題なく行えます。書き出したJSONは `raw.githubusercontent.com` 経由で配信され、
そちらはCORSが許可されているため、静的なダッシュボードHTMLから直接読み込めます。

## セットアップ手順

1. このリポジトリ（`yomitan-typhoon-data`、**Public**）をGitHub上に作成する。
2. このフォルダの中身一式（`.github/`, `scripts/`, `data/`, `README.md`）をそのままpushする。
3. GitHubの Settings → Actions → General → Workflow permissions を
   **"Read and write permissions"** に変更して保存する（Actionsがコミット・pushできるようにするため）。
4. Actionsタブ → "Update Yomitan Outage Data" ワークフロー → "Run workflow" で一度手動実行し、
   `data/yomitan_outage.json` が正しく更新されることを確認する。
5. 以降は15分ごとに自動実行される。

## データの参照URL

```
https://raw.githubusercontent.com/yomitanvillage/yomitan-typhoon-data/main/data/yomitan_outage.json
```

## 注意点

- GitHub Actionsのscheduled workflowは、リポジトリに60日間動きがないと自動的に無効化されます。
  その場合はActionsタブから再度有効化してください。
- cronのタイミングはGitHub側の負荷状況により数分前後することがあります。
