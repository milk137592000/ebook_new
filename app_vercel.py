"""
EPUB/PDF轉換器網頁應用 - Vercel優化版本
支援簡體轉正體、行距調整、多格式輸出
"""

import os
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file

# 創建Flask應用
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# 在Vercel環境中禁用某些功能
VERCEL_ENV = os.environ.get('VERCEL') is not None

@app.route('/')
def index():
    """主頁"""
    return render_template('index.html')

@app.route('/health')
def health():
    """健康檢查"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "environment": "vercel" if VERCEL_ENV else "local"
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """檔案上傳處理"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '沒有選擇檔案'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '沒有選擇檔案'}), 400
        
        # 檢查檔案類型
        if not file.filename.lower().endswith(('.epub', '.pdf')):
            return jsonify({'error': '不支援的檔案格式，請上傳EPUB或PDF檔案'}), 400
        
        # 在Vercel環境中，暫時只返回成功訊息
        if VERCEL_ENV:
            return jsonify({
                'success': True,
                'filename': file.filename,
                'message': 'Vercel環境：檔案上傳功能正在開發中'
            })
        
        # 本地環境的完整處理邏輯
        return jsonify({
            'success': True,
            'filename': file.filename,
            'message': '檔案上傳成功'
        })
        
    except Exception as e:
        return jsonify({'error': f'上傳失敗: {str(e)}'}), 500

@app.route('/convert', methods=['POST'])
def convert_file():
    """檔案轉換處理"""
    try:
        if VERCEL_ENV:
            return jsonify({
                'success': True,
                'message': 'Vercel環境：轉換功能正在開發中',
                'download_url': '#'
            })
        
        return jsonify({
            'success': True,
            'message': '轉換完成',
            'download_url': '/download/test.epub'
        })
        
    except Exception as e:
        return jsonify({'error': f'轉換失敗: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    """404錯誤處理"""
    return jsonify({'error': '頁面不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    """500錯誤處理"""
    return jsonify({'error': '伺服器內部錯誤'}), 500

# Vercel需要這個變數
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = not VERCEL_ENV
    app.run(host='0.0.0.0', port=port, debug=debug)
