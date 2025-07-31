"""
EPUB/PDF轉換器網頁應用 - Render優化版本
支援簡體轉正體、行距調整、多格式輸出
"""

import os
import shutil
import tempfile
import zipfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename

# 禁用可能有問題的依賴
MAGIC_AVAILABLE = False

from core.epub_processor import EpubProcessor
from core.pdf_processor import PdfProcessor
from core.markdown_processor import MarkdownProcessor

# 創建Flask應用
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# 確保輸出目錄存在
UPLOAD_FOLDER = 'static/outputs'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
        "environment": "render"
    })

@app.route('/status')
def status():
    """系統狀態"""
    # 檢查PDF處理器是否可用
    pdf_available = True
    try:
        from core.pdf_processor import PdfProcessor
    except ImportError:
        pdf_available = False

    return jsonify({
        "status": "running",
        "text_converter": "OpenCC簡繁轉換器已就緒",
        "pdf_processor_available": pdf_available,
        "message": "EPUB轉換器運行中 (Render環境)"
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
        filename = secure_filename(file.filename)
        if not filename.lower().endswith(('.epub', '.pdf')):
            return jsonify({'error': '不支援的檔案格式，請上傳EPUB或PDF檔案'}), 400
        
        # 儲存檔案
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, safe_filename)
        file.save(filepath)
        
        # 檢測檔案類型
        file_type = 'epub' if filename.lower().endswith('.epub') else 'pdf'
        file_size = os.path.getsize(filepath)
        
        return jsonify({
            'success': True,
            'filename': safe_filename,
            'original_filename': filename,
            'file_type': file_type,
            'file_size': file_size,
            'message': '檔案上傳成功'
        })
        
    except Exception as e:
        return jsonify({'error': f'上傳失敗: {str(e)}'}), 500

@app.route('/convert', methods=['POST'])
def convert_file():
    """檔案轉換處理"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        line_height = data.get('line_height', 1.6)
        output_format = data.get('output_format', 'epub')
        convert_simplified = data.get('convert_simplified', False)
        
        if not filename:
            return jsonify({'error': '沒有指定檔案'}), 400
        
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(input_path):
            return jsonify({'error': '檔案不存在'}), 404
        
        # 根據檔案類型選擇處理器
        if filename.lower().endswith('.epub'):
            processor = EpubProcessor(line_height=line_height)
            
            # 載入EPUB
            if not processor.load_epub(input_path):
                return jsonify({'error': '載入EPUB檔案失敗'}), 400
            
            # 修改格式
            processor.modify_epub_format()
            
            # 簡繁轉換
            conversion_stats = None
            if convert_simplified:
                conversion_stats = processor.convert_text()
            
            # 儲存結果
            output_filename = f"converted_{processor.book.get_metadata('DC', 'title')[0].title if processor.book.get_metadata('DC', 'title') else 'book'}.{output_format}"
            output_path = os.path.join(UPLOAD_FOLDER, output_filename)
            
            if output_format == 'epub':
                success = processor.save_epub(output_path)
            else:  # markdown
                md_processor = MarkdownProcessor()
                success = md_processor.epub_to_markdown(processor.book, output_path)
            
            if not success:
                return jsonify({'error': '儲存檔案失敗'}), 500
            
            # 獲取書籍資訊
            book_info = {
                'title': processor.book.get_metadata('DC', 'title')[0].title if processor.book.get_metadata('DC', 'title') else '未知',
                'author': processor.book.get_metadata('DC', 'creator')[0].title if processor.book.get_metadata('DC', 'creator') else '未知',
                'language': processor.book.get_metadata('DC', 'language')[0].title if processor.book.get_metadata('DC', 'language') else '未知'
            }
            
            return jsonify({
                'success': True,
                'message': '轉換完成',
                'download_url': f'/download/{output_filename}',
                'output_filename': output_filename,
                'book_info': book_info,
                'conversion_stats': conversion_stats
            })
            
        else:  # PDF
            try:
                pdf_processor = PdfProcessor()

                # PDF只能轉換為Markdown
                if output_format != 'md':
                    return jsonify({'error': 'PDF檔案只能轉換為Markdown格式'}), 400

                # 轉換PDF為Markdown
                output_filename = f"converted_{os.path.splitext(os.path.basename(filename))[0]}.md"
                output_path = os.path.join(UPLOAD_FOLDER, output_filename)

                success = pdf_processor.pdf_to_markdown(input_path, output_path)

                if not success:
                    return jsonify({'error': '轉換PDF失敗'}), 500

                return jsonify({
                    'success': True,
                    'message': '轉換完成',
                    'download_url': f'/download/{output_filename}',
                    'output_filename': output_filename,
                    'book_info': {
                        'title': os.path.splitext(os.path.basename(filename))[0],
                        'author': '未知',
                        'language': '未知'
                    },
                    'conversion_stats': None
                })

            except ImportError:
                return jsonify({'error': 'PDF處理器不可用，請檢查依賴安裝'}), 500
            except Exception as e:
                return jsonify({'error': f'PDF轉換失敗: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'轉換失敗: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """檔案下載"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': '檔案不存在'}), 404
        
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': f'下載失敗: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    """404錯誤處理"""
    return jsonify({'error': '頁面不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    """500錯誤處理"""
    return jsonify({'error': '伺服器內部錯誤'}), 500

# Render需要這個變數
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
