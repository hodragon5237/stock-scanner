import streamlit as st
import pandas as pd
from stock_agent import get_korean_tickers, fetch_stock_data, analyze_strategy
import time

st.set_page_config(page_title="음봉타법 트레이딩 대시보드", layout="centered", initial_sidebar_state="expanded")

# --- Custom CSS for Trendy, Mobile-First UI ---
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    html, body, [class*="css"]  {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        font-size: 16px; /* Base font size increased for mobile */
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: #121212;
        color: #F5F5F7;
    }
    [data-testid="stSidebar"] {
        background-color: #1A1A1A;
        border-right: none;
    }
    
    h1 {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        letter-spacing: -1.5px;
        font-size: 2rem !important;
        margin-bottom: 0px !important;
        padding-bottom: 10px !important;
    }
    
    h2, h3 {
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* Modern Toss-style Card Design */
    .invest-card {
        background: #1E1E1E;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        border: 1px solid #333333;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .invest-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        border: 1px solid #4a4a4a;
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 12px;
        border-bottom: 1px solid #333;
        padding-bottom: 10px;
    }
    
    .stock-name {
        font-size: 1.25rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
    }
    
    .stock-code {
        font-size: 0.9rem;
        color: #888888;
        margin-left: 8px;
    }
    
    .stock-price {
        font-size: 1.1rem;
        font-weight: 600;
        color: #eb5374; /* Accent red for price */
    }
    
    .reason-badge {
        display: inline-block;
        background: rgba(49, 130, 206, 0.15);
        color: #63B3ED;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 14px;
    }
    
    .action-box {
        background: #2D2D2D;
        padding: 14px;
        border-radius: 8px;
        font-size: 1rem;
        color: #E2E8F0;
        font-weight: 500;
        line-height: 1.4;
    }
    
    /* Highlights for Actions */
    .action-buy { border-left: 4px solid #48BB78; }
    .action-sell { border-left: 4px solid #F56565; }
    .action-hold { border-left: 4px solid #ECC94B; }
    
    /* Guide Panel formatting */
    .guide-box {
        background: #1A1A1A;
        border-radius: 16px;
        padding: 24px;
        margin-top: 40px;
        border: 1px solid #333;
    }
    
    /* Neon Button */
    .stButton > button {
        background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 700;
        font-size: 1.05rem;
        width: 100%;
        box-shadow: 0 4px 14px 0 rgba(0, 114, 255, 0.39);
    }
    .stButton > button:hover {
        opacity: 0.9;
    }
    
    hr {
        border-color: #333;
    }
</style>
""", unsafe_allow_html=True)
# -----------------------------------------------------------

st.title("🕯️ 음봉타법 스캐너")
st.markdown("<p style='color:#888; font-size:1.1rem; margin-top:-10px; margin-bottom:20px;'>유튜브에서 검증된 주식 매매 기법, 오늘 살 만한 종목을 편하게 찾아보세요.</p>", unsafe_allow_html=True)

# Sidebar settings
st.sidebar.header("⚙️ 스캔 설정")
scan_limit = st.sidebar.slider("시가총액 상위 스캔 종목 수", min_value=10, max_value=200, value=50, step=10)

def render_card(row, action_type):
    border_class = "action-buy"
    if "손절" in row['대응 액션'] or "익절" in row['대응 액션']:
        border_class = "action-sell"
    elif "보유" in row['대응 액션'] or "관망" in row['상태']:
        border_class = "action-hold"
        
    html = f"""<div class="invest-card">
<div class="card-header">
<div>
<span class="stock-name">{row['종목명']}</span>
<span class="stock-code">{row['종목코드']}</span>
</div>
<div class="stock-price">{int(row['현재가']):,}원</div>
</div>
<div class="reason-badge">💡 {row['사유']}</div>
<div class="action-box {border_class}">
🚩 <b>대응:</b> {row['대응 액션']}
</div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)

if st.sidebar.button("지금 스캔하기"):
    with st.spinner(f"시가총액 상위 {scan_limit}개 종목 데이터를 분석하는 중입니다... 잠시만 기다려주세요."):
        tickers_df = get_korean_tickers(limit=scan_limit)
        
        progress_bar = st.progress(0)
        results = []
        
        for i, row in tickers_df.iterrows():
            ticker = row['Code']
            name = row['Name']
            
            df = fetch_stock_data(ticker)
            if df is not None:
                res = analyze_strategy(ticker, name, df)
                results.append(res)
            else:
                results.append({"종목코드": ticker, "종목명": name, "상태": "오류", "사유": "데이터 불러오기 실패", "대응 액션": "-", "현재가": 0})
                
            progress = int(((i + 1) / scan_limit) * 100)
            progress_bar.progress(progress)
            
        res_df = pd.DataFrame(results)
        
        # 1. Recommended Stocks Output
        st.markdown("### ✅ 오늘 당장 주목할 종목 (매수 고려)")
        recommended = res_df[res_df["상태"].str.contains("추천", na=False)]
        
        if recommended.empty:
             st.info("오늘은 음봉타법 기준에 완벽하게 부합하는 신규 매수 종목이 없습니다. 현금 관망을 추천합니다.")
        else:
             for idx, row in recommended.iterrows():
                 render_card(row, "buy")
                 
        st.markdown("<br>", unsafe_allow_html=True)
                 
        # 2. Take Profit / Stop Loss Output
        st.markdown("### ⚠️ 보유 중이라면 필독 (익절 / 손절)")
        holding = res_df[res_df["상태"].str.contains("관망 / 매도 고려", na=False)]
        
        if holding.empty:
             st.info("과거 추천 종목 중 오늘 당장 익절이나 손절 처리가 필요한 종목이 없습니다.")
        else:
             for idx, row in holding.iterrows():
                 render_card(row, "sell")

        st.markdown("<br>", unsafe_allow_html=True)
                 
        # 3. Rejected Stocks Output (Kept as simple expander to save space on mobile)
        with st.expander("❌ 구경만 하세요 (제외된 종목 리스트)"):
             rejected = res_df[res_df["상태"] == "제외됨"]
             st.dataframe(rejected[["종목명", "사유"]], use_container_width=True, hide_index=True)

else:
    st.info("👈 스캔할 종목 수를 설정하고 버튼을 누르시면 시장을 분석해 최고의 종목을 뽑아드립니다.")

# --- Bottom Guide Panel (Mobile Friendly) ---
st.markdown("""<div class="guide-box">
<h3 style='margin-top:0px;'>💡 가이드: 사유 및 대응 전략</h3>
<p style='color:#48BB78; font-weight:700; margin-bottom:4px;'>🟢 신규 매수 타이밍</p>
<ul style='font-size:1rem; color:#ccc;'>
<li><b>1음봉 타법</b>: 기준봉 다음 날 음봉 발생. <b>5일선 터치 시 매수</b></li>
<li><b>2음봉 타법</b>: 기준봉 후 이틀 연속 하락. <b>2일차 종가 혹은 3일차 시가 매수</b></li>
<li><b>3음봉 타법</b>: 기준봉 후 3연속 하락. <b>4일차 상승(양봉) 시 매수</b></li>
<li><b>D-Day 타법</b>: 거래량 마른 작은 도지 캔들. <b>도지의 고점을 돌파할 때 맹추격 매수</b></li>
</ul>
<p style='color:#ECC94B; font-weight:700; margin-top:20px; margin-bottom:4px;'>⚠️ 기 보유자 대응 (과거 타점 이력)</p>
<ul style='font-size:1rem; color:#ccc;'>
<li><b style='color:#F56565'>익절 권장 (+5%)</b>: 과거 타점 진입 후 +5% 이상 도달. <b>수익 실현(매도) 고려</b></li>
<li><b>보유 관망 중</b>: 과거 타점 이후 기준 이탈 없이 순항 중. <b>+5% 갈 때까지 보유</b></li>
<li><b style='color:#F56565'>손절</b>: 주가가 생명선을 깨고 하락. <b>즉시 전량 매도 (손절)</b></li>
</ul>
<p style='color:#888; font-weight:700; margin-top:20px; margin-bottom:4px;'>❌ 매수 금지 구간</p>
<ul style='font-size:1rem; color:#888;'>
<li><b>정배열 아님</b>: 추세가 꺾여 역배열이거나 정배열이 아님.</li>
<li><b>장대양봉 없음</b>: 세력의 수급(기준봉)이 없음.</li>
<li><b>장대양봉 이후 거래량 불만족</b>: 눌림목 구간에서 거래량이 터짐(세력 이탈).</li>
</ul>
</div>""", unsafe_allow_html=True)
