# EPUB/PDF轉換器 - 網頁版

這是一個功能強大的EPUB/PDF格式轉換網頁應用程式，支援簡體轉正體中文、閱讀方向調整、行距設定和多格式輸出。

## 🚀 一鍵部署

### Heroku 部署
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/milk137592000/ebook_new)

### Vercel 部署
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/milk137592000/ebook_new)

### Railway 部署
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/milk137592000/ebook_new)

## 🌟 功能特色

- 📖 **多格式支援**：支援EPUB和PDF檔案輸入
- 🔄 **簡體轉正體**：自動檢測並轉換簡體中文為正體中文
- 📐 **閱讀方向轉換**：將直向閱讀改為橫向閱讀
- 📏 **行距調整**：可自由調整文字行距（1.0-3.0倍）
- 🔤 **字型優化**：更改字型為微軟正黑體
- 📱 **多格式輸出**：支援EPUB和Markdown格式輸出
- 🌐 **網頁介面**：現代化的網頁操作介面
- 📚 **Obsidian相容**：生成適合Obsidian的階層化Markdown
- 🎯 **拖拽上傳**：支援拖拽檔案上傳
- ⚡ **即時處理**：快速轉換和下載

## 🔧 系統需求

- Python 3.7+
- 現代網頁瀏覽器（Chrome、Firefox、Safari、Edge）
- macOS / Windows / Linux

## 🚀 快速開始

### 方法一：一鍵啟動（推薦）

```bash
# 下載專案後，直接執行啟動腳本
./run_web.sh
```

### 方法二：手動啟動

1. **創建虛擬環境**：
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows
```

2. **安裝依賴**：
```bash
pip install -r requirements.txt
```

3. **啟動網頁應用**：
```bash
python app.py
```

4. **開啟瀏覽器**：
   訪問 http://localhost:5001

## 📱 使用方法

### 步驟1：上傳檔案
- 拖拽EPUB或PDF檔案到上傳區域
- 或點擊「選擇檔案」按鈕
- 支援最大100MB的檔案

### 步驟2：設定選項
- **行距**：調整文字行距（建議1.4-2.0）
- **簡繁轉換**：自動檢測並轉換簡體中文
- **輸出格式**：
  - **EPUB**：修改後的電子書格式
  - **Markdown**：適合Obsidian的階層化格式

### 步驟3：轉換和下載
- 點擊「開始轉換」
- 等待處理完成
- 下載轉換後的檔案

## Calibre安裝（可選）

如果您需要轉換為MOBI或PDF格式，請安裝Calibre：

### macOS
```bash
# 使用Homebrew
brew install --cask calibre

# 或下載安裝包
# https://calibre-ebook.com/download_osx
```

### Windows
下載並安裝：https://calibre-ebook.com/download_windows

### Linux
```bash
# Ubuntu/Debian
sudo apt-get install calibre

# 或使用官方安裝腳本
sudo -v && wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sudo sh /dev/stdin
```

## 使用方法

1. 啟動應用程式後，您會看到圖形化介面
2. 點擊「選擇EPUB檔案」選擇要轉換的檔案
3. 選擇輸出格式：
   - **EPUB**：修改後的EPUB檔案
   - **MOBI**：適用於Kindle的格式（需要Calibre）
   - **PDF**：PDF格式（需要Calibre）
4. 選擇輸出位置
5. 點擊「開始轉換」

## 測試

專案包含一個測試EPUB檔案生成器：

```bash
# 創建測試用的直向EPUB檔案
python create_test_epub.py

# 然後使用應用程式轉換這個檔案
```

## 專案結構

```
epub-converter/
├── main.py                    # 主程式入口
├── run.sh                     # 啟動腳本
├── create_test_epub.py        # 測試檔案生成器
├── gui/
│   ├── __init__.py
│   └── main_window.py         # GUI介面
├── core/
│   ├── __init__.py
│   ├── epub_processor.py      # EPUB處理核心
│   └── format_converter.py    # 格式轉換
├── utils/
│   ├── __init__.py
│   └── helpers.py             # 輔助函數
├── requirements.txt           # Python依賴
├── README.md                  # 說明文件
└── venv/                      # 虛擬環境（自動創建）
```

## 轉換效果

### 轉換前（直向閱讀）
- 文字方向：由右至左，由上到下
- 字型：預設字型（通常是serif）
- 翻頁：可能不符合現代閱讀習慣

### 轉換後（橫向閱讀）
- 文字方向：由左至右，由上到下
- 字型：微軟正黑體（Microsoft JhengHei）
- 翻頁：左側上一頁，右側下一頁
- 相容性：適合現代電子書閱讀器

## 支援的格式

| 輸入格式 | 輸出格式 | 說明 |
|---------|---------|------|
| EPUB | EPUB | 修改後的EPUB檔案，保持原有結構 |
| EPUB | MOBI | Amazon Kindle專用格式（需要Calibre） |
| EPUB | PDF | 便攜式文件格式（需要Calibre） |

## 故障排除

### 常見問題

**Q: 啟動時出現「缺少依賴套件」錯誤**
A: 請確保已安裝所有Python依賴：
```bash
pip install -r requirements.txt
```

**Q: 無法轉換為MOBI或PDF格式**
A: 請安裝Calibre軟體，並確保`ebook-convert`命令可用：
```bash
# 檢查Calibre是否正確安裝
ebook-convert --version
```

**Q: 轉換後的檔案無法開啟**
A: 請檢查：
1. 原始EPUB檔案是否有效
2. 輸出路徑是否有寫入權限
3. 磁碟空間是否足夠

**Q: 字型沒有正確顯示**
A: 微軟正黑體可能在某些系統上不可用，程式會自動使用備用字型。

**Q: macOS上出現Tk警告**
A: 這是正常現象，不影響功能。可以設定環境變數來隱藏警告：
```bash
export TK_SILENCE_DEPRECATION=1
```

### 日誌和除錯

如果遇到問題，請檢查：
1. 終端機輸出的錯誤訊息
2. 確保EPUB檔案格式正確
3. 檢查系統權限設定

## 技術細節

### CSS修改
程式會在EPUB中添加以下CSS樣式：
```css
html, body {
    writing-mode: horizontal-tb !important;
    direction: ltr !important;
    text-orientation: mixed !important;
}

* {
    font-family: "Microsoft JhengHei", "微軟正黑體", "PingFang TC", "Helvetica Neue", Arial, sans-serif !important;
}
```

### OPF檔案修改
程式會修改EPUB的OPF檔案，設定：
```xml
<spine page-progression-direction="ltr">
```

這確保了在Kindle等設備上正確的翻頁方向。

## 授權

本專案採用MIT授權條款。

## 貢獻

歡迎提交Issue和Pull Request來改善這個專案。

## 更新日誌

### v1.0.0
- 初始版本
- 支援EPUB直向轉橫向
- 字型更改為微軟正黑體
- 支援EPUB、MOBI、PDF輸出
- 圖形化使用者介面
