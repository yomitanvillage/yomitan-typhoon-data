#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沖縄電力の停電マップAPI（xml_map_koazaBetsu.php）から読谷村の停電状況を取得し、
data/yomitan_outage.json に書き出す。GitHub Actionsから定期実行される想定。

このAPIはブラウザからのCORSアクセスは拒否されるが、サーバー側からの通常のHTTP GETは
問題なく取得できることを確認済み。
"""

import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

XML_URL = "https://www.okidenmail.jp/bosai/api/xml_map_koazaBetsu.php"
OUTPUT_PATH = "data/yomitan_outage.json"
TARGET_TOWN_NAME = "読谷村"
JST = timezone(timedelta(hours=9))
TIMEOUT_SECONDS = 20


def fetch_xml_bytes() -> bytes:
    req = urllib.request.Request(XML_URL, headers={"User-Agent": "Mozilla/5.0 (yomitan-typhoon-data bot)"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as res:
        return res.read()


def build_data() -> dict:
    now_str = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
    try:
        raw = fetch_xml_bytes()
        root = ET.fromstring(raw)

        common = root.find("common_info")
        title = (common.findtext("title") or "").strip() if common is not None else ""
        source_datetime = (common.findtext("datetime") or "").strip() if common is not None else ""

        towns = [t for t in root.iter("town") if t.get("name") == TARGET_TOWN_NAME]

        entries = []
        total_houses = 0
        for town in towns:
            house_el = town.find("power_cut_house")
            if house_el is not None and house_el.text:
                try:
                    total_houses += int(house_el.text.strip())
                except ValueError:
                    pass
            for oaza in town.findall("oaza"):
                for koaza in oaza.findall("koaza"):
                    entries.append(
                        {
                            "area": koaza.get("name") or oaza.get("name") or "",
                            "houses": koaza.get("k_tdnNum") or "",
                            "status": koaza.get("k_status") or "",
                            "restore": koaza.get("k_restore") or "",
                            "occurredAt": f'{koaza.get("k_tdnDate", "")} {koaza.get("k_tdnTime", "")}'.strip(),
                        }
                    )

        data = {
            "ok": True,
            "updatedAt": now_str,
            "sourceTitle": title,
            "sourceDatetime": source_datetime,
            "totalHouses": total_houses,
            "entries": entries,
        }
    except Exception as e:  # noqa: BLE001 - 何が起きても失敗として記録し、既存ファイルを壊さない
        data = {
            "ok": False,
            "updatedAt": now_str,
            "error": str(e),
        }
    return data


def main() -> None:
    data = build_data()
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
