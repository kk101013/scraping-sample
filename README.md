# Webスクレイピング・データ収集（サンプル）

Webサイトの一覧ページを**全ページ自動で巡回**し、必要な項目を抜き出して
**CSV と Excel** に出力するサンプルです。
手作業でのコピペ収集を、再実行できるスクリプト1本に置き換えます。

> 対象は、スクレイピング学習用に公開されている公式の練習サイト
> [books.toscrape.com](https://books.toscrape.com/) です。
> スクレイピングの練習用として公開されているサイトを使用しています。
> **実案件では対象サイト・取得項目・出力形式をご要望に合わせて差し替えます。**

## できること

- 一覧ページの **ページ送り（次へ）を自動でたどり、全ページを巡回**（今回は50ページ）
- 各アイテムから **タイトル・価格・評価・在庫・商品URL** を抽出
- 価格を数値に（`£51.77` → `51.77`）、評価を数値に（`Three` → `3`）正規化
- 結果を **CSV（Excelで開いても文字化けしない UTF-8）** と **Excel** に出力
- **取得件数・失敗URL・所要時間をレポート**で報告
- 相手サーバへの配慮：アクセス間隔のウェイト・User-Agent明示・失敗時リトライ

## 実行結果（50ページ → 1,000件）

```
スクレイピング結果レポート
====================================
- 巡回ページ数 : 50 ページ
- 取得件数     : 1000 件
- 取得失敗     : 0 件
- 所要時間     : 約40〜50 秒
- 出力ファイル : books.csv / books.xlsx
```

出力CSV（先頭）：

| タイトル | 価格(GBP) | 評価 | 在庫 | 商品URL |
|---|---:|---:|---|---|
| A Light in the Attic | 51.77 | 3 | In stock | …/a-light-in-the-attic_1000/ |
| Tipping the Velvet | 53.74 | 1 | In stock | …/tipping-the-velvet_999/ |
| Sapiens: A Brief History of Humankind | 54.23 | 5 | In stock | …/sapiens-…_996/ |

## ファイル構成

```
scraping-sample/
├─ scrape.py                 収集スクリプト
├─ output/
│  ├─ books.csv              取得データ（CSV / UTF-8）
│  ├─ books.xlsx             取得データ（Excel）
│  └─ scrape_report.txt      取得件数・失敗・所要時間のレポート
└─ README.md                 このファイル
```

## 使い方

```bash
pip install -r requirements.txt
python scrape.py
```

## 技術メモ

- HTTP取得: `requests`（Session・User-Agent・タイムアウト・リトライ）
- HTML解析: `BeautifulSoup`（CSSセレクタで要素を抽出）
- ページ送り: `li.next a` を再帰的にたどり、なくなったら終了
- 整形・出力: `pandas`（CSVは `utf-8-sig` でExcel文字化け回避、Excelは openpyxl）
- マナー: アクセス間隔のウェイト（既定0.5秒）、`robots.txt`・各サイトの利用規約の遵守を前提
- 環境: Python 3 / requests / beautifulsoup4 / pandas / openpyxl

## このサンプルの位置づけ（収集 → 整形 → 集計）

- **収集**：本サンプル（スクレイピング）
- **整形**：[data-cleaning-sample](https://github.com/kk101013/data-cleaning-sample)（表記ゆれ・重複の統一）
- **集計**：[sales-report-sample](https://github.com/kk101013/sales-report-sample)（集計・グラフ化）

集めて → 整えて → 集計する、までを一気通貫で対応できます。

---
*取得対象サイト・項目・ページ構造・出力形式（CSV/Excel/JSON）は、ご要望に合わせて調整できます。
ログインが必要なサイトや、JavaScriptで描画されるサイトは、規約・取得可否を確認したうえで個別に相談します。*
