import yfinance as yf
import pandas as pd
import logging
from datetime import datetime
import os
from analyzer import calculate_macd_and_signals
from config import OUTPUT_DIR

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

def fetch_wantgoo_data(target_date_str=None):
    """
    真實連線版：透過 Yahoo Finance 獲取真實台股數據。
    加入 target_date_str (YYYY-MM-DD) 來實現「時光機」歷史回溯計算功能。
    """
    logging.info(f"開始連線 Yahoo Finance 擷取真實台股數據... (目標日期: {target_date_str or '今日'})")
    
    tw_stocks = {
        "2330": "台積電", "2317": "鴻海", "2454": "聯發科", 
        "2881": "富邦金", "2603": "長榮", "2308": "台達電",
        "2891": "中信金", "2382": "廣達", "3231": "緯創"
    }
    
    results = []
    
    for code, name in tw_stocks.items():
        try:
            ticker = yf.Ticker(f"{code}.TW")
            # 抓取過去一年的數據，確保我們有足夠的歷史資料可以切換
            df = ticker.history(period="1y")
            
            if df.empty:
                continue
                
            df.index = df.index.tz_localize(None)
            
            # 【時光機核心邏輯】：如果有指定過去的日期，就把該日期「之後」的未來數據全部切除！
            if target_date_str:
                target_date = pd.to_datetime(target_date_str)
                df = df[df.index <= target_date]
            
            # 再次檢查切除後剩下的資料夠不夠算 MACD
            if len(df) < 60:
                logging.warning(f"{name} ({code}) 歷史資料不足 60 筆，無法計算該日 MACD，略過。")
                continue
                
            signal = calculate_macd_and_signals(df, code)
            
            # 取得「當時」的收盤價
            current_price = round(df['Close'].iloc[-1], 2)
            
            if signal:
                results.append({
                    "股票代碼": code,
                    "股票名稱": name,
                    "現在價格": current_price,
                    "技術指標狀態": signal
                })
                
        except Exception as e:
            logging.error(f"抓取 {name} ({code}) 時發生錯誤: {e}")

    # 整理結果並存檔
    results_df = pd.DataFrame(results)
    if not results_df.empty:
        results_df = results_df.sort_values(by="股票代碼", ascending=True).reset_index(drop=True)
    
    # 決定存檔日期名稱
    if target_date_str:
        file_date_str = pd.to_datetime(target_date_str).strftime("%Y%m%d")
    else:
        file_date_str = datetime.now().strftime("%Y%m%d")
        
    export_to_excel(results_df, file_date_str)
    
    return results_df

def export_to_excel(df, date_str):
    if df.empty:
        return
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    filename = f"{date_str}_真實技術分析.xlsx"
    filepath = os.path.join(OUTPUT_DIR, filename)
    df.to_excel(filepath, sheet_name="MACD交叉篩選報告", index=False)
    logging.info(f"成功導出真實 Excel 檔至 {filepath}")