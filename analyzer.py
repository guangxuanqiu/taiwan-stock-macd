import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

def calculate_macd_and_signals(df, stock_code):
    """
    運算 MACD 並判斷交叉訊號。
    傳入的 df 必須包含 'Close' (收盤價) 且依日期舊到新排序。
    """
    # 歷史K線不足之防禦：不足60筆則跳過並發出警告 [cite: 66, 67]
    if len(df) < 60:
        logging.warning(f"股票 {stock_code} 歷史 K 線資料不足 60 筆，自動跳過分析。")
        return None
    
    # 1. 計算12日指數移動平均線:EMA(12) [cite: 43]
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    # 2. 計算26日指數移動平均線:EMA(26) [cite: 44]
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    # 3. 計算快線(差離值): DIF=EMA(12) - EMA(26) [cite: 45]
    df['DIF'] = df['EMA_12'] - df['EMA_26']
    # 4. 計算慢線(訊號線):MACD_Line = EMA(DIF, 9) [cite: 46]
    df['MACD_Line'] = df['DIF'].ewm(span=9, adjust=False).mean()

    # 取得今日與前一日的數值
    today = df.iloc[-1]
    yesterday = df.iloc[-2]

    # 黃金交叉 (Golden Cross): DIF_{t-1} <= MACD_Line_{t-1} 且 DIF_t > MACD_Line_t [cite: 48]
    if yesterday['DIF'] <= yesterday['MACD_Line'] and today['DIF'] > today['MACD_Line']:
        return "黃金交叉"
    
    # 死亡交叉 (Death Cross): DIF_{t-1} >= MACD_Line_{t-1} 且 DIF_t < MACD_Line_t [cite: 51]
    elif yesterday['DIF'] >= yesterday['MACD_Line'] and today['DIF'] < today['MACD_Line']:
        return "死亡交叉"
    
    return None