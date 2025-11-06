# -*- coding: utf-8 -*-
"""
KOSPI 연속 상승 종목 Top N
출력 포맷(기본 compact): [연속상승일수 순위, 종목명, 종가, 상승가격, '상승률%']
- 연속상승일수 내림차순으로 정렬, 동률이면 오늘 등락률(%) 내림차순
- 상승가격/상승률은 '오늘' 기준(전일 대비)

의존성: pykrx, pandas, tzdata
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
        d = base - timedelta(days=i)
        ds = yyyymmdd(datetime(d.year, d.month, d.day))
        try:
            df = stock.get_market_ohlcv_by_ticker(ds, market="KOSPI")
            if df is not None and not df.empty and "종가" in df.columns:
                return datetime(d.year, d.month, d.day)
        except Exception:
            pass
    raise RuntimeError("최근 거래일 데이터를 찾지 못했습니다.")


def get_recent_trading_dates(n: int, end_dt: datetime) -> list[datetime]:
    """end_dt 포함, 과거로 n개 거래일을 수집(오래된→최신 순서로 리턴)."""
    dates, d = [], end_dt
    while len(dates) < n:
        ds = yyyymmdd(d)
        try:
            df = stock.get_market_ohlcv_by_ticker(ds, market="KOSPI")
            if df is not None and not df.empty and "종가" in df.columns:
                dates.append(d)
        except Exception:
            pass
        d -= timedelta(days=1)
    dates.sort()
    return dates


def calc_streak_and_today_change(dates: list[datetime]):
    """
    dates: 오래된→최신 순 거래일 리스트.
    return: DataFrame[ticker] = {streak, close(오늘), pct(오늘%), change(오늘 상승가)}
    """
    # 연속상승 계산(종가 기준)
    prev_close = {}
    streak = {}

    for i, dt in enumerate(dates):
        ds = yyyymmdd(dt)
        df = stock.get_market_ohlcv_by_ticker(ds, market="KOSPI")
        df["종가"] = pd.to_numeric(df["종가"], errors="coerce")

        if i == 0:
            prev_close = df["종가"].to_dict()
            # 첫날은 비교 대상이 없으니 0으로 시작
            streak = {t: 0 for t in df.index}
            continue

        today_close = df["종가"].to_dict()
        for t, c in today_close.items():
            p = prev_close.get(t)
            if pd.notna(c) and pd.notna(p):
                if c > p:
                    streak[t] = streak.get(t, 0) + 1
                else:
                    streak[t] = 0
            else:
                streak[t] = 0
        prev_close = today_close

    # 오늘 데이터 + 전일 종가로 상승가/상승률 계산
    today = dates[-1]
    prev  = dates[-2]
    ds_today, ds_prev = yyyymmdd(today), yyyymmdd(prev)

    df_today = stock.get_market_ohlcv_by_ticker(ds_today, market="KOSPI")
    df_prev  = stock.get_market_ohlcv_by_ticker(ds_prev,  market="KOSPI")

    for col in ("종가", "등락률"):
        if col in df_today.columns:
            df_today[col] = pd.to_numeric(df_today[col], errors="coerce")
    df_prev["종가"] = pd.to_numeric(df_prev["종가"], errors="coerce")

    merged = df_today[["종가", "등락률"]].rename(columns={"종가": "close", "등락률": "pct"})
    merged = merged.join(df_prev[["종가"]].rename(columns={"종가": "prev_close"}), how="left")

    # prev_close가 없으면 pct로 역산
    miss = merged["prev_close"].isna() & merged["close"].notna() & merged["pct"].notna()
    if miss.any():
        merged.loc[miss, "prev_close"] = merged.loc[miss, "close"] / (1 + merged.loc[miss, "pct"] / 100)

    merged["change"] = merged["close"] - merged["prev_close"]

    # streak 값 붙이기
    merged["streak"] = pd.Series(streak)
    # 유효 데이터만
    merged = merged.dropna(subset=["close", "pct", "change", "streak"])

    # 티커 → 종목명
    names = {}
    for t in merged.index:
        try:
            names[t] = stock.get_market_ticker_name(t)
        except Exception:
            names[t] = t
    merged["name"] = pd.Series(names)

    # 숫자형 정리
    merged["close"]  = merged["close"].round(0).astype(int)
    merged["change"] = merged["change"].round(0).astype(int)
    merged["pct"]    = merged["pct"].astype(float)
    merged["streak"] = merged["streak"].astype(int)

    return merged


def main():
    ap = argparse.ArgumentParser(description="연속 상승일수 순위 TopN → JSON")
    ap.add_argument("--out", default="out", help="JSON 저장 폴더")
    ap.add_argument("--top", type=int, default=10, help="Top N (기본 10)")
    ap.add_argument("--format", choices=["compact","object"], default="compact",
                    help="compact=[rankByStreak,name,price,change,'pct%'], object={...}")
    ap.add_argument("--decimals", type=int, default=1, help="퍼센트 소수 자리수 (기본 1)")
    args = ap.parse_args()

    today = find_latest_trading_date()
    dates = get_recent_trading_dates(n=8, end_dt=today)
    df = calc_streak_and_today_change(dates)

    # 정렬: streak ↓, pct ↓
    df_sorted = df.sort_values(by=["streak", "pct"], ascending=[False, False]).head(args.top)

    # 결과 패킹
    if args.format == "compact":
        items = [
            [i + 1, row["name"], row["close"], row["change"], f'{row["pct"]:.{args.decimals}f}%']
            for i, (_, row) in enumerate(df_sorted.iterrows())
        ]
        schema = ["rankByStreak", "name", "price", "change", "pctChange"]
    else:
        items = [
            {"rankByStreak": i + 1, "name": row["name"], "price": int(row["close"]),
             "change": int(row["change"]), "pctChange": float(row["pct"])}
            for i, (_, row) in enumerate(df_sorted.iterrows())
        ]
        schema = None

    payload = {
        "asOf": yyyy_mm_dd(today),
        "market": "KOSPI",
        "count": len(items),
        "items": items
    }
    if schema:
        payload["schema"] = schema

    os.makedirs(args.out, exist_ok=True)
    dated  = os.path.join(args.out, f"consecutive_ranked_{yyyy_mm_dd(today)}.json")
    latest = os.path.join(args.out, "consecutive_ranked_latest.json")

    with open(dated, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    with open(latest, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"[OK] saved: {dated}")
    print(f"[OK] saved: {latest}")


if __name__ == "__main__":
    main()