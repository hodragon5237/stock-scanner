import FinanceDataReader as fdr
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import streamlit as st

@st.cache_data(ttl=3600*12)
def get_korean_tickers(limit: int = 100) -> pd.DataFrame:
    """Fetches the top N Korean stocks by Market Cap from KRX."""
    krx = fdr.StockListing('KRX')
    # Use Marcap if available, or just take the top rows. Usually KRX listing is sorted by Marcap.
    # Return code and name
    return krx.head(limit)[['Code', 'Name']]

@st.cache_data(ttl=3600*12)
def fetch_stock_data(ticker: str) -> Optional[pd.DataFrame]:
    try:
        # Trading days only happen 5 days a week, plus holidays.
        # To guarantee 120 trading days, we need at least 200 calendar days. We will fetch 250 days.
        start_date = datetime.now() - timedelta(days=250)
        df = fdr.DataReader(ticker, start_date)
        if df.empty:
            return None
        return df
    except Exception as e:
        return None

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()
    df['MA120'] = df['Close'].rolling(window=120).mean()
    
    # Is it aligned (정배열)?
    df['IsAligned'] = (df['MA5'] > df['MA20']) & (df['MA20'] > df['MA60']) & (df['MA60'] > df['MA120'])
    return df

def analyze_strategy(ticker: str, name: str, df: pd.DataFrame) -> dict:
    base_result = {"종목코드": str(ticker), "종목명": str(name), "상태": "제외됨", "사유": "", "대응 액션": "-", "현재가": 0.0}
    
    if len(df) < 120:
        base_result["사유"] = "데이터 부족 (120영업일 미만)"
        return base_result
        
    df = calculate_indicators(df)
    today_close = float(df['Close'].iloc[-1])
    today_ma5 = float(df['MA5'].iloc[-1])
    base_result["현재가"] = today_close
    
    # Check alignment for the most recent day
    if not df['IsAligned'].iloc[-1]:
        base_result["사유"] = "정배열 아님"
        return base_result
        
    recent_idx = len(df) - 20
    found_standard_candle = False
    
    best_pattern = None
    best_action = None
    
    for i in range(recent_idx, len(df)):
        prev_close = df['Close'].iloc[i-1]
        close = df['Close'].iloc[i]
        open_price = df['Open'].iloc[i]
        
        daily_change = (close - prev_close) / prev_close
        is_yang = close > open_price
        
        # Standard Candle Criteria
        if is_yang and daily_change > 0.10: 
            found_standard_candle = True
            base_vol = df['Volume'].iloc[i]
            base_mid = (open_price + close) / 2 
            
            # Check days following the standard candle
            for j in range(i + 1, len(df)):
                days_since = j - i
                
                yin_count = 0
                for k in range(i + 1, j + 1):
                    if df['Close'].iloc[k] < df['Open'].iloc[k]:
                        yin_count += 1
                    else:
                        break
                        
                j_close = df['Close'].iloc[j]
                j_open = df['Open'].iloc[j]
                j_low = df['Low'].iloc[j]
                j_high = df['High'].iloc[j]
                j_ma5 = df['MA5'].iloc[j]
                j_vol = df['Volume'].iloc[j]
                
                buy_signal = ""
                
                if days_since == 1 and yin_count == 1:
                    if j_low <= j_ma5 * 1.02 and j_close >= j_ma5 * 0.98: 
                        buy_signal = "1음봉 타법"
                elif days_since == 2 and yin_count == 2:
                    buy_signal = "2음봉 타법"
                elif days_since == 3 and yin_count == 3:
                    buy_signal = "3음봉 타법 (매수 대기)"
                elif days_since == 4 and yin_count >= 2:
                    if j_close > j_open:
                        buy_signal = "3음봉 타법 (조건충족)"
                
                body_size = abs(j_close - j_open) / j_open
                if days_since >= 1 and body_size < 0.02 and j_vol < base_vol * 0.4:
                    buy_signal = "D-Day 타법 (도지)"
                
                if buy_signal:
                    if j == len(df) - 1:
                        # buy signal triggered today
                        best_pattern = buy_signal
                        if "D-Day" in buy_signal:
                            best_action = f"매수 준비: 고점({j_high:,.0f}원) 돌파 시 매수"
                        else:
                            best_action = "매수 고려: 조건 만족 완료"
                    else:
                        # buy signal triggered in the past
                        # Evaluate what happened from day j+1 to today
                        max_high_since = df['High'].iloc[j+1:].max() if j+1 < len(df) else j_high
                        
                        if max_high_since >= j_close * 1.05:
                            best_pattern = f"{buy_signal} (과거 매수)"
                            best_action = f"익절 권장: +5% 이상 도달 (고가 {max_high_since:,.0f}원 기록)"
                        elif today_close < today_ma5:
                            best_pattern = f"{buy_signal} (과거 매수)"
                            best_action = "손절: 현재 5일선 이탈 상태"
                        elif today_close < base_mid:
                            best_pattern = f"{buy_signal} (과거 매수)"
                            best_action = "손절: 장대양봉 중심선 이탈"
                        else:
                            best_pattern = f"{buy_signal} (과거 매수)"
                            best_action = f"보유 관망 중 (현재가: {today_close:,.0f}원, 목표 +5%)"

    if best_pattern:
        if "익절" in best_action or "손절" in best_action or "보유" in best_action:
            base_result["상태"] = "관망 / 매도 고려"
        else:
            base_result["상태"] = "추천 (매수 고려)"
        base_result["사유"] = best_pattern
        base_result["대응 액션"] = best_action
    elif found_standard_candle:
        base_result["사유"] = "장대양봉 발견됨 (현재 매수/매도 시점 아님)"
    else:
        base_result["사유"] = "최근 20일 이내 기준봉(장대양봉) 없음"
        
    return base_result

