#!/bin/bash

# EPUB格式轉換器啟動腳本

echo "正在啟動EPUB格式轉換器..."

# 檢查虛擬環境是否存在
if [ ! -d "venv" ]; then
    echo "創建虛擬環境..."
    python3 -m venv venv
fi

# 啟動虛擬環境
source venv/bin/activate

# 檢查依賴是否已安裝
if ! python -c "import ebooklib" 2>/dev/null; then
    echo "安裝依賴套件..."
    pip install -r requirements.txt
fi

# 設定環境變數以抑制Tk警告
export TK_SILENCE_DEPRECATION=1

# 啟動應用程式
echo "啟動GUI介面..."
python main.py
