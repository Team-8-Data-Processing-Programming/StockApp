# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict
from pykrx import stock
import pandas as pd
import math

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 시장 현황 =====
INDEX_MAP = {
    "KOSPI":  {"symbol": "^KS11"},
    "KOSDAQ": {"symbol": "^KQ11"},
    "NASDAQ": {"symbol": "^IXIC"},
}

def last_price_and_change(symbol: str):
    tkr = yf.Ticker(symbol)
    df = tkr.history(period="10d", interval="1d", auto_adjust=False).dropna()
    if len(df) == 0:
        return None, None
    closes = df["Close"].astype(float)
    prev_close = float(closes.iloc[-2]) if len(closes) >= 2 else float(closes.iloc[-1])
    last_close = float(closes.iloc[-1])
    pct = ((last_close - prev_close) / prev_close * 100.0) if prev_close else 0.0
    return round(last_close, 2), round(pct, 2)

@app.get("/market/summary")
def market_summary():
    result = []
    for idx, (name, meta) in enumerate(INDEX_MAP.items(), start=1):
        value, change = last_price_and_change(meta["symbol"])
        if value is None:
            continue
        result.append({"id": str(idx), "name": name, "value": value, "change": change})
    return {"data": result}

# ===== 공통 유틸 =====
def today(fmt="%Y%m%d"):
    return datetime.now().strftime(fmt)

def kospi_ohlcv(d=None):
    base = datetime.now() if d is None else datetime.strptime(d, "%Y%m%d")
    for k in range(0, 6):  # 당일부터 최대 5일 전까지 영업일 fallback
        dd = (base - timedelta(days=k)).strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_ticker(dd, market="KOSPI")
        if df is not None and not df.empty:
            return df
    return stock.get_market_ohlcv_by_ticker(today(), market="KOSPI")

def recent_bdays(n=4, max_back_days: int = 120) -> list[str]:
    dates = []
    day = 0
    while len(dates) < n and day < max_back_days:  # 충분히 뒤로 탐색
        d = (datetime.now() - timedelta(days=day)).strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_ticker(d, market="KOSPI")
        if df is not None and not df.empty:
            dates.append(d)
        day += 1
    return sorted(dates)[-n:]

def _as_int(x, default=0):
    try:
        return default if x is None or (isinstance(x, float) and math.isnan(x)) else int(x)
    except Exception:
        return default

def _as_float(x, default=0.0):
    try:
        return default if x is None or (isinstance(x, float) and math.isnan(x)) else float(x)
    except Exception:
        return default

def to_items(df: pd.DataFrame, top: int = 10) -> List[Dict]:
    out = []
    df = df.copy()
    if "등락률" in df.columns:
        df["등락률"] = df["등락률"].fillna(0)
    for i, (ticker, row) in enumerate(df.head(top).iterrows(), start=1):
        name = stock.get_market_ticker_name(ticker)
        out.append({
            "id": str(i),
            "ticker": ticker,
            "name": name,
            "price": _as_int(row.get("종가", 0)),
            "change": _as_float(row.get("지표", row.get("등락률", 0.0))),
            "volume": _as_int(row.get("거래량", 0)),
            "value": _as_int(row.get("거래대금", row.get("값", 0))),  # 거래대금/거래량 등 금액성 보조 값
        })
    return out

# ===== 카테고리 엔드포인트 =====

# 1) 상승률 TOP10
@app.get("/screen/top-gainers")
def screen_top_gainers(limit: int = 10, min_price: int = 1000):
    df = kospi_ohlcv()
    df = df[(df["종가"] >= min_price) & (df["거래량"] > 0)]
    if "등락률" in df.columns:
        df = df[df["등락률"].notna()]
    df = df.sort_values("등락률", ascending=False)
    df = df.assign(지표=df["등락률"])
    return {"data": to_items(df, top=limit)}

# 2) 하락률 TOP10
@app.get("/screen/top-losers")
def screen_top_losers(limit: int = 10, min_price: int = 1000):
    df = kospi_ohlcv()
    df = df[(df["종가"] >= min_price) & (df["거래량"] > 0)]
    if "등락률" in df.columns:
        df = df[df["등락률"].notna()]
    df = df.sort_values("등락률", ascending=True)  # 오름차순: 가장 많이 하락
    df = df.assign(지표=df["등락률"])
    return {"data": to_items(df, top=limit)}

# 3) 거래량 급증 TOP10 (전일 대비 증가율로 정렬)
@app.get("/screen/volume-surge")
def screen_volume_surge(limit: int = 10, min_price: int = 1000):
    ds = recent_bdays(2)
    if len(ds) < 2:
        return {"data": []}
    d_prev, d_today = ds[-2], ds[-1]
    prev = stock.get_market_ohlcv_by_ticker(d_prev, market="KOSPI")[["거래량"]].rename(columns={"거래량":"V_prev"})
    today_df = stock.get_market_ohlcv_by_ticker(d_today, market="KOSPI")
    df = prev.join(today_df, how="inner")
    df = df[(df["종가"] >= min_price) & (df["거래량"] > 0) & (df["V_prev"] > 0)]
    df = df.assign(증가율=(df["거래량"] / df["V_prev"] - 1.0) * 100.0)
    df = df.sort_values("증가율", ascending=False)
    # 정렬 지표는 증가율, 표시값은 거래량(주)
    df = df.assign(지표=df["증가율"], 값=df["거래량"])
    return {"data": to_items(df, top=limit)}

# 4) 3일 연속 상승 TOP10 (C0 < C1 < C2 < 오늘 종가)
@app.get("/screen/three-up")
def screen_three_up(limit: int = 10, min_price: int = 1000):
    ds = recent_bdays(4)
    if len(ds) < 4:
        return {"data": []}
    d0, d1, d2, d3 = ds
    c0 = stock.get_market_ohlcv_by_ticker(d0, market="KOSPI")[["종가"]].rename(columns={"종가":"C0"})
    c1 = stock.get_market_ohlcv_by_ticker(d1, market="KOSPI")[["종가"]].rename(columns={"종가":"C1"})
    c2 = stock.get_market_ohlcv_by_ticker(d2, market="KOSPI")[["종가"]].rename(columns={"종가":"C2"})
    t3 = stock.get_market_ohlcv_by_ticker(d3, market="KOSPI")  # 오늘
    df = c0.join(c1, how="inner").join(c2, how="inner").join(t3, how="inner")
    df = df[(df["종가"] >= min_price) & (df["거래량"] > 0)]
    df = df[(df["C0"] < df["C1"]) & (df["C1"] < df["C2"]) & (df["C2"] < df["종가"])]
    if "등락률" in df.columns:
        df = df[df["등락률"].notna()].sort_values("등락률", ascending=False)
    df = df.assign(지표=df["등락률"])
    return {"data": to_items(df, top=limit)}

# 5) 급락 후 반등 TOP10
@app.get("/screen/bounce-after-plunge")
def screen_bounce_after_plunge(limit: int = 10, min_price: int = 1000, plunge_pct: float = -3.0):
    ds = recent_bdays(2)
    if len(ds) < 2:
        return {"data": []}
    d_prev, d_today = ds[-2], ds[-1]

    prev = stock.get_market_ohlcv_by_ticker(d_prev, market="KOSPI")[["등락률"]]\
            .rename(columns={"등락률": "R_prev"})
    today_df = stock.get_market_ohlcv_by_ticker(d_today, market="KOSPI")[["종가", "거래량", "거래대금", "등락률"]]\
            .rename(columns={"등락률": "R_today"})

    df = prev.join(today_df, how="inner")
    df = df[(df["종가"] >= min_price) & (df["거래량"] > 0)]
    df = df[df["R_prev"].notna() & df["R_today"].notna()]
    df = df[(df["R_prev"] <= plunge_pct) & (df["R_today"] > 0)]
    df = df.sort_values("R_today", ascending=False).assign(지표=lambda x: x["R_today"])
    return {"data": to_items(df, top=limit)}

# 6) 거래대금 TOP10
@app.get("/screen/top-by-trading-value")
def screen_top_by_trading_value(limit: int = 10):
    df = kospi_ohlcv().sort_values("거래대금", ascending=False)
    df = df.assign(지표=df["거래대금"])  
    return {"data": to_items(df, top=limit)}

# 7) 안정적 우량주 TOP10
@app.get("/screen/stable-bluechips")
def screen_stable_bluechips(
    limit: int = 10,
    top_n_mc: int = 200,         # 시총 상위 범위
    min_price: int = 1000,
    lookback_days: int = 20,     # 변동성 산정 구간(영업일)
):
    import numpy as np

    # 최근 영업일 (시총, 현재가 기준일)
    last_bday = recent_bdays(1, max_back_days=365)[-1]

    # 시총 상위 추출
    cap = stock.get_market_cap_by_ticker(last_bday, market="KOSPI")
    if cap is None or cap.empty or "시가총액" not in cap.columns:
        return {"data": []}
    cap = cap.sort_values("시가총액", ascending=False).head(top_n_mc)

    # 변동성 계산 기간 (영업일 lookback_days를 커버하도록 여유 있게 -60일)
    # pykrx는 날짜 문자열 'YYYYMMDD'
    base_dt = datetime.strptime(last_bday, "%Y%m%d")
    start_dt = (base_dt - timedelta(days=60))  # 충분히 여유
    start = start_dt.strftime("%Y%m%d")
    end = last_bday

    rows = []
    # 각 티커별로 기간 데이터 조회 → 최근 lookback_days 영업일만 잘라서 수익률 std 계산
    for ticker in cap.index.tolist():
        try:
            df = stock.get_market_ohlcv_by_date(start, end, ticker)
            if df is None or df.empty or "종가" not in df.columns:
                continue
            # 최근 lookback_days만 사용 (영업일 개수 충분치 않으면 스킵)
            if len(df) < lookback_days + 1:
                continue

            # 뒤에서 N개만 사용
            df_tail = df.tail(lookback_days + 1)
            # 일간 수익률(%) 계산
            close = df_tail["종가"].astype(float)
            rets = close.pct_change().dropna() * 100.0
            if len(rets) < lookback_days:
                continue

            vol_std = float(rets.std(ddof=0))  # 표준편차 (%)
            last_row = df_tail.iloc[-1]
            price = float(last_row["종가"])
            volume = int(last_row.get("거래량", 0))
            value = int(last_row.get("거래대금", 0))

            if price >= min_price and volume > 0:
                rows.append({
                    "ticker": ticker,
                    "VOL_STD": vol_std,
                    "종가": price,
                    "거래량": volume,
                    "거래대금": value,
                })
        except Exception:
            # 개별 티커 에러는 그냥 스킵
            continue

    if not rows:
        return {"data": []}

    # 낮은 변동성 순 정렬 후 상위 limit
    out_df = pd.DataFrame(rows).sort_values("VOL_STD", ascending=True)
    
    # ticker를 인덱스로 세팅 
    if "ticker" in out_df.columns:
        out_df = out_df.set_index("ticker")


    # to_items로 변환 (지표=VOL_STD)
    out_df = out_df.assign(지표=out_df["VOL_STD"])
    return {"data": to_items(out_df, top=limit)}

# 8) 배당수익률 TOP10 (DIV 내림차순)
@app.get("/screen/dividend-yield")
def screen_dividend_yield(limit: int = 10, min_price: int = 1000):
    d = today()
    ohlcv = kospi_ohlcv(d)
    f = stock.get_market_fundamental(d, market="KOSPI")
    df = ohlcv.join(f, how="inner")
    col = "DIV" if "DIV" in df.columns else None
    if col is None:
        return {"data": []}
    df = df[(df[col] > 0) & (df["종가"] >= min_price) & (df["거래량"] > 0)]
    df = df.sort_values(col, ascending=False).assign(지표=lambda x: x[col])
    return {"data": to_items(df, top=limit)}

# 9) 저 PER TOP10
@app.get("/screen/low-per")
def screen_low_per(limit: int = 10, min_price: int = 1000):
    d = today()
    ohlcv = kospi_ohlcv(d)
    f = stock.get_market_fundamental(d, market="KOSPI")
    df = ohlcv.join(f, how="inner")
    df = df[(df["PER"] > 0) & (df["종가"] >= min_price) & (df["거래량"] > 0)]
    df = df[df["PER"].notna()].sort_values("PER", ascending=True).assign(지표=lambda x: x["PER"])
    return {"data": to_items(df, top=limit)}

# 10) 저 PBR TOP10
@app.get("/screen/low-pbr")
def screen_low_pbr(limit: int = 10, min_price: int = 1000):
    d = today()
    ohlcv = kospi_ohlcv(d)
    f = stock.get_market_fundamental(d, market="KOSPI")
    df = ohlcv.join(f, how="inner")
    df = df[(df["PBR"] > 0) & (df["종가"] >= min_price) & (df["거래량"] > 0)]
    df = df[df["PBR"].notna()].sort_values("PBR", ascending=True).assign(지표=lambda x: x["PBR"])
    return {"data": to_items(df, top=limit)}
