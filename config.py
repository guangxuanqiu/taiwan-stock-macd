import os

# 輸出路徑設定
OUTPUT_DIR = "./outputs/" # Excel 報表自動輸出與儲存之終端機本地目錄 [cite: 28, 60]

# 模擬 User-Agent 輪替名單 [cite: 40]
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

# 重試機制參數 [cite: 65]
MAX_RETRIES = 3
RETRY_DELAY = 5