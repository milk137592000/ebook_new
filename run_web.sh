#!/bin/bash

# EPUB/PDF轉換器網頁版啟動腳本

echo "🚀 正在啟動EPUB/PDF轉換器網頁版..."

# 檢查虛擬環境是否存在
if [ ! -d "venv" ]; then
    echo "📦 創建虛擬環境..."
    python3 -m venv venv
fi

# 啟動虛擬環境
source venv/bin/activate

# 檢查依賴是否已安裝
if ! python -c "import flask" 2>/dev/null; then
    echo "📥 安裝依賴套件..."
    pip install -r requirements.txt
fi

# 設定環境變數
export TK_SILENCE_DEPRECATION=1

# 創建必要目錄
mkdir -p static/uploads static/outputs

echo "🌐 啟動網頁服務器..."
echo "📱 請在瀏覽器中訪問: http://localhost:5001"
echo "⏹️  按 Ctrl+C 停止服務器"
echo ""

# 啟動Flask應用
python app.py
