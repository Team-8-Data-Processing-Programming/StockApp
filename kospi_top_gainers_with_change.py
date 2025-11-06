# -*- coding: utf-8 -*-
"""
오늘 가장 많이 오른 KOSPI 종목 Top 10을
[순위, 종목명, 종가, 상승가격, 상승률%] 형식으로 JSON 저장
"""

import argparse, json, os
from datetime import datetime, timedelta
import pandas as pd
from pykrx import stock

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None


def now_kst():
    try:
        return datetime.now(ZoneInfo("Asia/Seoul")) if ZoneInfo else datetime.now()
    except Exception:
        return datetime.now()


def yyyymmdd(d: datetime) -> str:
    return d.strftime("%Y%m%d")


def yyyy_mm_dd(d: datetime) -> str:
    return d.strftime("%Y-%m-%d")


def find_latest_trading_date(max_back_days: int = 10) -> datetime:
    base = now_kst().date()
    for i in range(max_back_days + 1):
        try_date = base - timedelta(days=i)
        ds = yyyymmdd(datetime(try_date.year, try_date.month, try_date.day))
        try:
            df = stock.get_market_ohlcv_by_ticker(ds, market="KOSPI")
            if df is not None and not df.empty and "등락률" in df.columns:
                return datetime(try_date.year, try_date.month, try_date.day)
        except Exception:
            continue
    raise RuntimeError("최근 거래일 데이터를 찾지 못했습니다.")


def get_top_gainers_with_change(target_dt: datetime, top_n: int = 10):
    ds = yyyymmdd(target_dt)
    df = stock.get_market_ohlcv_by_ticker(ds, market="KOSPI")

    if df is None or df.empty:
        raise RuntimeError(f"KOSPI 데이터가 없습니다: {ds}")

    df = df.dropna(subset=["등락률", "종가"])
    df["종가"] = pd.to_numeric(df["종가"], errors="coerce")
    df["등락률"] = pd.to_numeric(df["등락률"], errors="coerce")

    df = df[df["등락률"] > 0]

    # 상승가격 = 종가 * (등락률 / (100 + 등락률))
    df["상승가격"] = (df["종가"] * (df["등락률"] / (100 + df["등락률"]))).round(0).astype(int)

    df_sorted = df.sort_values(by="등락률", ascending=False).head(top_n)

    result = []
    for idx, (ticker, row) in enumerate(df_sorted.iterrows(), start=1):
        name = stock.get_market_ticker_name(ticker)
        result.append([
            idx,
            name,
            int(row["종가"]),
            int(row["상승가격"]),
            f"{row['등락률']:.1f}%"  # 상승률(문자열)
        ])
    return result


def main():
    ap = argparse.ArgumentParser(description="KOSPI Top 상승 종목 (상승가격 포함) → JSON")
    ap.add_argument("--out", default="out", help="JSON 저장 폴더 (기본: out)")
    ap.add_argument("--top", type=int, default=10, help="Top N (기본 10)")
    args = ap.parse_args()

    target_dt = find_latest_trading_date()
    items = get_top_gainers_with_change(target_dt, args.top)

    payload = {
        "asOf": yyyy_mm_dd(target_dt),
        "market": "KOSPI",
        "count": len(items),
        "schema": ["rank", "name", "price", "change", "pctChange"],
        "items": items
    }

    os.makedirs(args.out, exist_ok=True)
    dated = os.path.join(args.out, f"kospi_top_gainers_with_change_{yyyy_mm_dd(target_dt)}.json")
    latest = os.path.join(args.out, "kospi_top_gainers_with_change_latest.json")

    with open(dated, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    with open(latest, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"[OK] saved: {dated}")
    print(f"[OK] saved: {latest}")


if __name__ == "__main__":
    main()
