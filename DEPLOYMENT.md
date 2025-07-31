# 部署指南

## Heroku 部署

### 方法1: 使用Heroku CLI

1. 安裝 Heroku CLI
2. 登入 Heroku：
   ```bash
   heroku login
   ```

3. 創建 Heroku 應用：
   ```bash
   heroku create your-app-name
   ```

4. 推送代碼：
   ```bash
   git push heroku main
   ```

### 方法2: 使用GitHub自動部署

1. 登入 [Heroku Dashboard](https://dashboard.heroku.com/)
2. 點擊 "New" -> "Create new app"
3. 輸入應用名稱
4. 在 "Deployment method" 選擇 "GitHub"
5. 連接到 `milk137592000/ebook_new` 倉庫
6. 啟用 "Automatic deploys" 從 main 分支

### 方法3: 一鍵部署

點擊下面的按鈕直接部署到Heroku：

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/milk137592000/ebook_new)

## Vercel 部署

1. 登入 [Vercel](https://vercel.com/)
2. 點擊 "New Project"
3. 導入 GitHub 倉庫 `milk137592000/ebook_new`
4. 配置環境變數（如果需要）
5. 點擊 "Deploy"

## Railway 部署

1. 登入 [Railway](https://railway.app/)
2. 點擊 "New Project"
3. 選擇 "Deploy from GitHub repo"
4. 選擇 `milk137592000/ebook_new` 倉庫
5. Railway 會自動檢測並部署

## 環境變數

部署時可能需要設置的環境變數：

- `FLASK_ENV`: 設為 `production`
- `PORT`: 由平台自動設置
- `FLASK_APP`: 設為 `app.py`

## 注意事項

1. 確保所有依賴都在 `requirements.txt` 中
2. 生產環境會自動禁用 debug 模式
3. 檔案上傳大小限制可能因平台而異
4. 某些平台可能有執行時間限制

## 本地測試生產配置

```bash
export FLASK_ENV=production
export PORT=5000
python app.py
```
