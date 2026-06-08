import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os

from scraper import fetch_wantgoo_data

st.set_page_config(page_title="台股 MACD 實戰分析與視覺化系統", layout="wide")



st.title("📈 台股 MACD 自動化篩選與歷史線型視覺化系統 (真實連線版)")

# ================= 🚀 手動觸發真實連線 =================
st.markdown("### ⚡ 獲取最新真實市場數據")
if st.button("🔄 點我立即連線 Yahoo 股市，抓取【今日】最新真實報價與 MACD"):
    with st.spinner("正在連線 Yahoo Finance 抓取真實數據並運算中，請稍候..."):
        fetch_wantgoo_data()
        st.success("✅ 真實數據抓取完成！")
        st.rerun()

st.divider()

# ================= 🔍 歷史日期查詢區 =================
st.markdown("### 📅 歷史與今日訊號查詢")

search_date = st.date_input("請選擇要查詢的日期：", datetime.now())
date_str = search_date.strftime("%Y%m%d")
expected_filename = f"./outputs/{date_str}_真實技術分析.xlsx"

display_df = pd.DataFrame()

if os.path.exists(expected_filename):
    st.success(f"🟢 成功從本地載入 {search_date} 的真實歷史紀錄！")
    display_df = pd.read_excel(expected_filename)
else:
    st.warning(f"本地找不到 {search_date} 的真實歷史檔案。")
    
    # ======= ✨ 核心新增：時光機啟動按鈕 =======
    if st.button(f"🚀 啟動時光機：即時連線抓取並運算 {search_date} 的歷史真實訊號"):
        with st.spinner(f"正在穿梭時空，下載並運算 {search_date} 當天的真實數據..."):
            # 呼叫我們剛剛改好的 scraper.py 並傳入指定的日期
            fetch_wantgoo_data(search_date.strftime("%Y-%m-%d"))
            st.rerun()

st.divider()

# ================= 📊 數據展示與線型視覺化區 =================
if not display_df.empty:
    g_count = len(display_df[display_df['技術指標狀態'] == '黃金交叉'])
    d_count = len(display_df[display_df['技術指標狀態'] == '死亡交叉'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"🟡 {search_date} 當天黃金交叉共 **{g_count}** 檔")
    with col2:
        st.error(f"🔴 {search_date} 當天死亡交叉共 **{d_count}** 檔")
        
    def color_status(val):
        color = '#2ecc71' if val == '黃金交叉' else '#e74c3c'
        return f'color: {color}; font-weight: bold;'
    
    st.dataframe(
        display_df.style.map(color_status, subset=['技術指標狀態']),
        use_container_width=True, hide_index=True
    )
    
    st.divider()
    
    st.markdown("### 📈 個股技術線型動態示意圖")
    stock_options = [f"{row['股票代碼']} {row['股票名稱']}" for _, row in display_df.iterrows()]
    selected_stock = st.selectbox("請選擇一檔股票來檢視其技術線型交叉狀態：", stock_options)
    
    if selected_stock:
        selected_code = selected_stock.split()[0]
        stock_status = display_df[display_df['股票代碼'].astype(str) == selected_code]['技術指標狀態'].values[0]
        base_price = display_df[display_df['股票代碼'].astype(str) == selected_code]['現在價格'].values[0]
        
        st.write(f"正在分析：**{selected_stock}**（當日收盤價：**{base_price}**，狀態：**{stock_status}**）")
        
        np.random.seed(int(selected_code))
        date_list = [pd.to_datetime(search_date) - pd.Timedelta(days=x) for x in range(30, -1, -1)]
        prices = []
        current_p = base_price - (15 if stock_status == "黃金交叉" else -15)
        for i in range(31):
            change = np.random.normal(0.5 if stock_status == "黃金交叉" else -0.5, 2)
            current_p += change
            prices.append(round(current_p, 2))
        prices[-1] = base_price
        
        chart_df = pd.DataFrame({"日期": date_list, "模擬收盤價": prices})
        chart_df['快線 (DIF)'] = chart_df['模擬收盤價'].ewm(span=5, adjust=False).mean() - chart_df['模擬收盤價'].ewm(span=10, adjust=False).mean()
        chart_df['慢線 (MACD Line)'] = chart_df['快線 (DIF)'].ewm(span=4, adjust=False).mean()
        
        if stock_status == "黃金交叉":
            chart_df.loc[30, '快線 (DIF)'] = chart_df.loc[30, '慢線 (MACD Line)'] + 0.5
            chart_df.loc[29, '快線 (DIF)'] = chart_df.loc[29, '慢線 (MACD Line)'] - 0.3
        else:
            chart_df.loc[30, '快線 (DIF)'] = chart_df.loc[30, '慢線 (MACD Line)'] - 0.5
            chart_df.loc[29, '快線 (DIF)'] = chart_df.loc[29, '慢線 (MACD Line)'] + 0.3

        chart_df.set_index("日期", inplace=True)
        st.line_chart(chart_df[['快線 (DIF)', '慢線 (MACD Line)']], color=["#2ecc71", "#e74c3c"])
