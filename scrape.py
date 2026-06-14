# -*- coding: utf-8 -*-
"""
Webスクレイピングのサンプル。

練習用に公開されているサンドボックスサイト books.toscrape.com から
書籍の一覧（タイトル・価格・評価・在庫）を全ページ巡回して収集し、
CSV と Excel に出力する。

- スクレイピング学習用に用意された練習サイトを対象にしているため、
  実案件より安全に動作確認しやすい。
- 実案件では「対象サイト・取得項目・出力形式」をご要望に合わせて差し替える。
"""

import time
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
import pandas as pd

# ---- 設定（案件ごとにここを書き換える） ---------------------------------
BASE_URL = "https://books.toscrape.com/catalogue/"
START_PAGE = "page-1.html"
REQUEST_INTERVAL = 0.5   # 連続アクセスの間隔（秒）。相手サーバへの負荷を抑える
TIMEOUT = 15             # 1リクエストのタイムアウト（秒）
MAX_RETRY = 3            # 失敗時のリトライ回数
USER_AGENT = "portfolio-scraper-sample/1.0 (educational use; contact: example@example.com)"

OUTPUT_DIR = Path(__file__).parent / "output"
CSV_PATH = OUTPUT_DIR / "books.csv"
XLSX_PATH = OUTPUT_DIR / "books.xlsx"
REPORT_PATH = OUTPUT_DIR / "scrape_report.txt"

# 評価（星）の英語表記 → 数値への変換表
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def fetch(url: str, session: requests.Session) -> str | None:
    """1ページ取得。失敗したらリトライし、それでもダメなら None を返す。"""
    for attempt in range(1, MAX_RETRY + 1):
        try:
            res = session.get(url, timeout=TIMEOUT)
            res.raise_for_status()
            res.encoding = res.apparent_encoding  # 文字化け対策
            return res.text
        except requests.RequestException as e:
            print(f"  ! 取得失敗 ({attempt}/{MAX_RETRY}): {url}  {e}", file=sys.stderr)
            time.sleep(REQUEST_INTERVAL * attempt)
    return None


def parse_books(html: str) -> list[dict]:
    """一覧ページのHTMLから書籍情報を抜き出す。"""
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for card in soup.select("article.product_pod"):
        link = card.select_one("h3 a")
        title = link.get("title", "").strip()
        detail_url = urljoin(BASE_URL, link.get("href", ""))

        # 価格（"£51.77" → 51.77）
        price_text = card.select_one("p.price_color").get_text(strip=True)
        price = float(price_text.replace("£", "").replace("Â", "").strip())

        # 評価（class="star-rating Three" の2語目を数値化）
        rating_class = card.select_one("p.star-rating")["class"]
        rating_word = next((c for c in rating_class if c != "star-rating"), "")
        rating = RATING_MAP.get(rating_word, None)

        # 在庫
        stock = card.select_one("p.instock.availability").get_text(strip=True)

        rows.append({
            "タイトル": title,
            "価格(GBP)": price,
            "評価": rating,
            "在庫": stock,
            "商品URL": detail_url,
        })
    return rows


def find_next_page(html: str) -> str | None:
    """ページ送りの「次へ」リンク（相対パス）を返す。なければ None。"""
    soup = BeautifulSoup(html, "html.parser")
    nxt = soup.select_one("li.next a")
    return nxt.get("href") if nxt else None


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    all_books: list[dict] = []
    failed_pages: list[str] = []
    page_count = 0
    next_page = START_PAGE
    start_time = time.time()

    print("スクレイピング開始 ...")
    while next_page:
        url = urljoin(BASE_URL, next_page)
        page_count += 1
        print(f"- ページ{page_count}: {url}")

        html = fetch(url, session)
        if html is None:
            failed_pages.append(url)
            break  # ページ送りが追えなくなるので中断

        all_books.extend(parse_books(html))
        next_page = find_next_page(html)
        time.sleep(REQUEST_INTERVAL)  # マナーとして毎回ウェイト

    elapsed = time.time() - start_time

    # ---- 出力 -----------------------------------------------------------
    df = pd.DataFrame(all_books)
    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")  # Excelで開いても文字化けしない
    df.to_excel(XLSX_PATH, index=False)

    # ---- レポート -------------------------------------------------------
    report = f"""スクレイピング結果レポート
====================================
- 巡回ページ数 : {page_count} ページ
- 取得件数     : {len(all_books)} 件
- 取得失敗     : {len(failed_pages)} 件
- 所要時間     : {elapsed:.1f} 秒
- 出力ファイル : {CSV_PATH.name} / {XLSX_PATH.name}
"""
    if failed_pages:
        report += "\n[取得に失敗したURL]\n" + "\n".join(f"  - {u}" for u in failed_pages) + "\n"

    REPORT_PATH.write_text(report, encoding="utf-8")
    print("\n" + report)
    print(f"完了: {len(all_books)} 件を {OUTPUT_DIR} に出力しました。")


if __name__ == "__main__":
    main()
