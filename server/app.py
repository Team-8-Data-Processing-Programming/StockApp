from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
    "KOSPI": {"symbol": "^KS11"},
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
def today(fmt: str = "%Y%m%d") -> str:
    return datetime.now().strftime(fmt)


def kospi_ohlcv(d: str | None = None) -> pd.DataFrame:
    base = datetime.now() if d is None else datetime.strptime(d, "%Y%m%d")
    for k in range(0, 6):  # 당일부터 최대 5일 전까지 영업일 fallback
        dd = (base - timedelta(days=k)).strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_ticker(dd, market="KOSPI")
        if df is not None and not df.empty:
            return df
    return stock.get_market_ohlcv_by_ticker(today(), market="KOSPI")


def recent_bdays(n: int = 4, max_back_days: int = 120) -> list[str]:
    dates: list[str] = []
    day = 0
    while len(dates) < n and day < max_back_days:
        d = (datetime.now() - timedelta(days=day)).strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_ticker(d, market="KOSPI")
        if df is not None and not df.empty:
            dates.append(d)
        day += 1
    return sorted(dates)[-n:]


def _as_int(x, default: int = 0) -> int:
    try:
        if x is None or (isinstance(x, float) and math.isnan(x)):
            return default
        return int(x)
    except Exception:
        return default


def _as_float(x, default: float = 0.0) -> float:
    try:
        if x is None or (isinstance(x, float) and math.isnan(x)):
            return default
        return float(x)
    except Exception:
        return default


def to_items(df: pd.DataFrame, top: int = 10) -> List[Dict]:
    out: List[Dict] = []
    df = df.copy()

    if "등락률" not in df.columns:
        df["등락률"] = 0.0
    df["등락률"] = df["등락률"].fillna(0)

    for i, (ticker, row) in enumerate(df.head(top).iterrows(), start=1):
        name = stock.get_market_ticker_name(ticker)
        out.append(
            {
                "id": str(i),
                "ticker": ticker,
                "name": name,
                "price": _as_int(row.get("종가", 0)),
                "change": _as_float(row["등락률"]),  
                "volume": _as_int(row.get("거래량", 0)),
                "value": _as_int(row.get("거래대금", row.get("값", 0))),
            }
        )
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
    return {"data": to_items(df, top=limit)}


# 2) 하락률 TOP10
@app.get("/screen/top-losers")
def screen_top_losers(limit: int = 10, min_price: int = 1000):
    df = kospi_ohlcv()
    df = df[(df["종가"] >= min_price) & (df["거래량"] > 0)]
    if "등락률" in df.columns:
        df = df[df["등락률"].notna()]
    df = df.sort_values("등락률", ascending=True)
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
    return {"data": to_items(df, top=limit)}


# 7) 안정적 우량주 TOP10  
@app.get("/screen/stable-bluechips")
def screen_stable_bluechips(limit: int = 10, top_n_mc: int = 200):
    d = today()

   
    cap = stock.get_market_cap_by_ticker(d, market="KOSPI")
    if cap is None or cap.empty or "시가총액" not in cap.columns:
        return {"data": []}

    ohlcv = kospi_ohlcv(d)

    cap_sorted = cap.sort_values("시가총액", ascending=False).head(top_n_mc)[["시가총액"]]
    cap_sorted = cap_sorted.rename(columns={"시가총액": "시총"})

    # 시총 + 오늘 시세 join 
    df = cap_sorted.join(ohlcv, how="inner")

    if "등락률" not in df.columns:
        df["등락률"] = 0.0
    df["등락률"] = df["등락률"].fillna(0.0)

    return {"data": to_items(df, top=limit)}

# 8) 배당수익률 TOP10
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
    df = df.sort_values(col, ascending=False)
    return {"data": to_items(df, top=limit)}


# 9) 저 PER TOP10
@app.get("/screen/low-per")
def screen_low_per(limit: int = 10, min_price: int = 1000):
    d = today()
    ohlcv = kospi_ohlcv(d)
    f = stock.get_market_fundamental(d, market="KOSPI")
    df = ohlcv.join(f, how="inner")
    df = df[(df["PER"] > 0) & (df["종가"] >= min_price) & (df["거래량"] > 0)]
    df = df[df["PER"].notna()].sort_values("PER", ascending=True)
    return {"data": to_items(df, top=limit)}


# 10) 저 PBR TOP10
@app.get("/screen/low-pbr")
def screen_low_pbr(limit: int = 10, min_price: int = 1000):
    d = today()
    ohlcv = kospi_ohlcv(d)
    f = stock.get_market_fundamental(d, market="KOSPI")
    df = ohlcv.join(f, how="inner")
    df = df[(df["PBR"] > 0) & (df["종가"] >= min_price) & (df["거래량"] > 0)]
    df = df[df["PBR"].notna()].sort_values("PBR", ascending=True)
    return {"data": to_items(df, top=limit)}


# 11) 주식 상세 보기
@app.get("/stock/detail")
def stock_detail(ticker: str):
    d = today()
    try:
        f_kospi = stock.get_market_fundamental(d, market="KOSPI")
        f_kosdaq = stock.get_market_fundamental(d, market="KOSDAQ")
        f = pd.concat([f_kospi, f_kosdaq])

        o_kospi = stock.get_market_ohlcv_by_ticker(d, market="KOSPI")
        o_kosdaq = stock.get_market_ohlcv_by_ticker(d, market="KOSDAQ")
        ohlcv = pd.concat([o_kospi, o_kosdaq])

        cap_kospi = stock.get_market_cap_by_ticker(d, market="KOSPI")
        cap_kosdaq = stock.get_market_cap_by_ticker(d, market="KOSDAQ")
        cap = pd.concat([cap_kospi, cap_kosdaq])

        if ticker not in f.index or ticker not in ohlcv.index:
            return JSONResponse(
                status_code=404,
                content={"error": "Ticker not found", "ticker": ticker},
            )

        row_f = f.loc[ticker]
        row_p = ohlcv.loc[ticker]

        market_cap_value = 0.0
        market_cap_text = "0원"

        if ticker in cap.index:
            val = cap.loc[ticker].get("시가총액", 0)
            if val and not math.isnan(val):
                market_cap_value = float(val)
                if market_cap_value >= 1e12:
                    market_cap_text = f"{market_cap_value / 1e12:.2f}조원"
                elif market_cap_value >= 1e8:
                    market_cap_text = f"{market_cap_value / 1e8:.0f}억원"
                elif market_cap_value >= 1e4:
                    market_cap_text = f"{market_cap_value / 1e4:.0f}만원"
                else:
                    market_cap_text = f"{market_cap_value:,.0f}원"

        def safe_get(row, key, default=0.0):
            val = row.get(key, default)
            if val is None or (isinstance(val, float) and math.isnan(val)):
                return default
            return float(val)

        roe_val = safe_get(row_f, "ROE", 0.0)
        if roe_val == 0.0 or math.isnan(roe_val):
            per_val = safe_get(row_f, "PER", 0.0)
            pbr_val = safe_get(row_f, "PBR", 0.0)
            if per_val > 0 and pbr_val > 0:
                roe_val = (pbr_val / per_val) * 100.0

        data = {
            "ticker": ticker,
            "name": stock.get_market_ticker_name(ticker),
            "price": safe_get(row_p, "종가", 0),
            "change": round(safe_get(row_p, "등락률", 0.0), 1),
            "marketCap": market_cap_text,
            "dividendYield": round(safe_get(row_f, "DIV", 0.0), 2),
            "pbr": round(safe_get(row_f, "PBR", 0.0), 2),
            "per": round(safe_get(row_f, "PER", 0.0), 2),
            "roe": round(roe_val, 2),
        }

        print(f"[DETAIL] {data}")
        return data

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "ticker": ticker})
