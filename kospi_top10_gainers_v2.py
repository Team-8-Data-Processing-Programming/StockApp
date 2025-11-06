# kospi_top10_gainers_v2.py
# KOSPI 당일 상승 상위 N개를 JSON으로 저장/표준출력
# - compact : [rank, name, price, change, 'pct%']
# - object  : {rank, name, price, change, pctChange}

import argparse
import json
import os
from datetime import datetime, timedelta

import pandas as pd

# ---- KST(Asia/Seoul) now() 편의 함수 -----------------------------------------
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None


def now_kst() -> datetime:
    try:
        return datetime.now(ZoneInfo("Asia/Seoul")) if ZoneInfo else datetime.now()
    except Exception:
        return datetime.now()


def yyyymmdd(d: datetime) -> str:
    return d.strftime("%Y%m%d")


def yyyy_mm_dd(d: datetime) -> str:
    return d.strftime("%Y-%m-%d")


# ---- pykrx 준비 ----------------------------------------------------------------
try:
    from pykrx import stock
except Exception:
    raise SystemExit(
        "pykrx가 설치되어 있지 않습니다. 먼저 "
        "`python -m pip install pandas pykrx tzdata` 를 실행하세요."
    )


# ---- 거래일 탐색 ---------------------------------------------------------------
def find_latest_trading_date(
    max_back_days: int = 10, on_or_before: datetime | None = None
) -> datetime:
    """최근 영업일(데이터가 존재하는 날짜) 찾기"""
    base = (on_or_before or now_kst()).date()
    for i in range(max_back_days + 1):
        d = base - timedelta(days=i)
        ds = d.strftime("%Y%m%d")
        try:
            df = stock.get_market_ohlcv_by_ticker(ds, market="KOSPI")
            if df is not None and not df.empty and "등락률" in df.columns:
                return datetime(d.year, d.month, d.day)
        except Exception:
            continue
    raise RuntimeError("최근 거래일 데이터를 찾지 못했습니다. 잠시 후 다시 시도해주세요.")


def prev_trading_date(target_dt: datetime) -> datetime:
    return find_latest_trading_date(on_or_before=target_dt - timedelta(days=1))


# ---- 랭킹 계산 ------------------------------------------------------------------
def get_ranked_items(
    target_dt: datetime, top_n: int = 10, sort_key: str = "pct"
) -> list[dict]:
    """
    해당 날짜의 KOSPI 상승 Top N을 dict 리스트로 반환
    - sort_key: 'pct' (상승률 순) 또는 'amount' (상승금액 순)
    """
    ds_today = yyyymmdd(target_dt)

    # 오늘 데이터
    df_today = stock.get_market_ohlcv_by_ticker(ds_today, market="KOSPI")
    if df_today is None or df_today.empty:
        raise RuntimeError(f"KOSPI 데이터가 비어있습니다: {ds_today}")

    # 수치형 변환
    for col in ("종가", "등락률"):
        if col in df_today.columns:
            df_today[col] = pd.to_numeric(df_today[col], errors="coerce")

    # 전일 종가 가져오기 (정확한 상승금액 계산)
    dt_prev = prev_trading_date(target_dt)
    ds_prev = yyyymmdd(dt_prev)
    df_prev = stock.get_market_ohlcv_by_ticker(ds_prev, market="KOSPI")
    if df_prev is not None and not df_prev.empty and "종가" in df_prev.columns:
        df_prev = df_prev[["종가"]].rename(columns={"종가": "prev_close"})
        df_prev["prev_close"] = pd.to_numeric(df_prev["prev_close"], errors="coerce")
        df = df_today.join(df_prev, how="left")
    else:
        df = df_today.copy()
        df["prev_close"] = pd.NA

    # 상승금액 계산: 기본은 전일 종가 사용, 없으면 등락률로 역산
    df["change"] = df["종가"] - df["prev_close"]
    mask = df["change"].isna() & df["종가"].notna() & df["등락률"].notna()
    if mask.any():
        # prev ≈ close / (1 + pct/100)
        prev_approx = df.loc[mask, "종가"] / (1.0 + df.loc[mask, "등락률"] / 100.0)
        df.loc[mask, "change"] = df.loc[mask, "종가"] - prev_approx

    # 정렬키 선택
    if sort_key == "amount":
        key = "change"
    else:
        key = "등락률"  # 기본: 상승률 순

    # 유효 데이터만
    df = df.dropna(subset=["종가", "등락률", "change"])

    # 상위 N
    df_sorted = df.sort_values(by=key, ascending=False).head(top_n)

    # 결과 빌드
    results: list[dict] = []
    for rank, (ticker, row) in enumerate(df_sorted.iterrows(), start=1):
        try:
            name = stock.get_market_ticker_name(ticker)
        except Exception:
            name = ticker

        close = int(round(row["종가"])) if pd.notna(row["종가"]) else None
        chg = int(round(row["change"])) if pd.notna(row["change"]) else None
        pct = float(row["등락률"]) if pd.notna(row["등락률"]) else None

        results.append(
            {
                "rank": rank,
                "name": name,
                "price": close,       # 종가
                "change": chg,        # 전일 대비 금액
                "pctChange": pct,     # 전일 대비 %
            }
        )
    return results


# ---- CLI / 저장 -----------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="KOSPI TopN Gainers -> JSON (pykrx)")
    ap.add_argument("--out", default="out", help="JSON 저장 폴더 (기본: out)")
    ap.add_argument("--top", type=int, default=10, help="Top N (기본 10)")
    ap.add_argument(
        "--format",
        choices=["compact", "object"],
        default="compact",
        help="compact: [rank,name,price,change,'xx.x%'], object: {..} (기본 compact)",
    )
    ap.add_argument("--schema", action="store_true", help="compact 포맷일 때 헤더 스키마 포함")
    ap.add_argument("--decimals", type=int, default=1, help="퍼센트 소수 자리수 (기본 1)")
    ap.add_argument("--no-print", action="store_true", help="STDOUT 출력 생략")
    ap.add_argument("--date", help="특정 날짜 지정 (YYYY-MM-DD). 없으면 최근 거래일 자동 탐색")
    ap.add_argument(
        "--sort",
        choices=["pct", "amount"],
        default="pct",
        help="정렬 기준: pct(상승률) / amount(상승금액). 기본 pct",
    )

    args = ap.parse_args()

    # 대상 날짜 결정
    if args.date:
        try:
            target_dt = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            raise SystemExit("날짜 형식이 올바르지 않습니다. 예: --date 2025-11-05")
        target_dt = find_latest_trading_date(on_or_before=target_dt)
    else:
        target_dt = find_latest_trading_date()

    # 데이터 수집
    objs = get_ranked_items(target_dt, top_n=args.top, sort_key=args.sort)

    # 포맷 변환
    if args.format == "compact":
        items = [
            [
                o["rank"],
                o["name"],
                o["price"],
                o["change"],
                (None if o["pctChange"] is None else f'{o["pctChange"]:.{args.decimals}f}%'),
            ]
            for o in objs
        ]
    else:
        items = objs

    payload = {
        "asOf": yyyy_mm_dd(target_dt),
        "market": "KOSPI",
        "count": len(items),
        "items": items,
    }
    if args.format == "compact" and args.schema:
        payload["schema"] = ["rank", "name", "price", "change", "pctChange"]

    # 저장
    os.makedirs(args.out, exist_ok=True)
    suffix = f"top{args.top}_{args.sort}_{args.format}"
    dated_path = os.path.join(args.out, f"kospi_{suffix}_{yyyy_mm_dd(target_dt)}.json")
    latest_path = os.path.join(args.out, f"kospi_{suffix}_latest.json")

    with open(dated_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    if not args.no_print:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"[OK] saved: {dated_path}")
    print(f"[OK] saved: {latest_path}")


if __name__ == "__main__":
    main()
