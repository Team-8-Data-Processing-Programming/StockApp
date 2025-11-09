from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Yahoo Finance 심볼 매핑
# KOSPI(코스피 종합) ^KS11, KOSDAQ(코스닥 종합) ^KQ11, NASDAQ Composite ^IXIC
INDEX_MAP = {
    "KOSPI":   {"symbol": "^KS11"},
    "KOSDAQ":  {"symbol": "^KQ11"},
    "NASDAQ":  {"symbol": "^IXIC"},
}

def last_price_and_change(symbol: str):
    """
    최근 일별 10개 데이터에서 마지막 두 개 종가로 등락률 계산
    return: (last_close, pct_change)  # pct_change는 % 값 (예: 0.6)
    """
    tkr = yf.Ticker(symbol)
    df = tkr.history(period="10d", interval="1d", auto_adjust=False)
    df = df.dropna()
    if len(df) == 0:
        return None, None
    closes = df["Close"].astype(float)

    if len(closes) >= 2:
        prev_close = float(closes.iloc[-2])
        last_close = float(closes.iloc[-1])
    else:
        prev_close = last_close = float(closes.iloc[-1])

    pct = ((last_close - prev_close) / prev_close * 100.0) if prev_close else 0.0
    return round(last_close, 2), round(pct, 2)

@app.get("/market/summary")
def market_summary():
    result = []
    for idx, (name, meta) in enumerate(INDEX_MAP.items(), start=1):
        value, change = last_price_and_change(meta["symbol"])
        if value is None:
            continue
        result.append({
            "id": str(idx),
            "name": name,
            "value": value,     # 지수 값
            "change": change    # 전일 대비 변화율(%) 예: 0.60, -0.46
        })
    return {"data": result}
