"""
EPUB/PDF轉換器網頁應用
支援簡體轉正體、行距調整、多格式輸出
"""

import os
import shutil
import tempfile
import zipfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
# 在雲端部署中禁用python-magic以避免依賴問題
MAGIC_AVAILABLE = False

from core.epub_processor import EpubProcessor
from core.pdf_processor import PdfProcessor
from core.text_converter import text_converter
from core.markdown_generator import MarkdownGenerator
from utils.helpers import validate_epub_file, get_file_size_mb

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/outputs'

# 確保目錄存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'epub', 'pdf'}


def allowed_file(filename):
    """檢查檔案類型是否允許"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def detect_file_type(file_path):
    """檢測檔案類型"""
    if MAGIC_AVAILABLE:
        try:
            mime = magic.Magic(mime=True)
            file_type = mime.from_file(file_path)

            if 'epub' in file_type or file_path.lower().endswith('.epub'):
                return 'epub'
            elif 'pdf' in file_type or file_path.lower().endswith('.pdf'):
                return 'pdf'
            else:
                return 'unknown'
        except:
            pass

    # 備用檢測方法（使用檔案副檔名）
    if file_path.lower().endswith('.epub'):
        return 'epub'
    elif file_path.lower().endswith('.pdf'):
        return 'pdf'
    else:
        return 'unknown'


@app.route('/')
def index():
    """主頁"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """處理檔案上傳"""
    if 'file' not in request.files:
        return jsonify({'error': '沒有選擇檔案'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '沒有選擇檔案'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 檢測檔案類型
        file_type = detect_file_type(file_path)
        file_size = get_file_size_mb(file_path)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'file_type': file_type,
            'file_size': f"{file_size:.1f} MB",
            'message': '檔案上傳成功'
        })
    
    return jsonify({'error': '不支援的檔案格式'}), 400


@app.route('/convert', methods=['POST'])
def convert_file():
    """處理檔案轉換"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        line_height = float(data.get('line_height', 1.6))
        output_format = data.get('output_format', 'epub')
        convert_simplified = data.get('convert_simplified', True)
        
        if not filename:
            return jsonify({'error': '沒有指定檔案'}), 400
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({'error': '檔案不存在'}), 404
        
        # 檢測檔案類型
        file_type = detect_file_type(file_path)
        
        # 創建輸出目錄
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], 
                                 f"converted_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(output_dir, exist_ok=True)
        
        result = {}
        
        if file_type == 'epub':
            result = process_epub_file(file_path, output_dir, line_height, 
                                     output_format, convert_simplified)
        elif file_type == 'pdf':
            result = process_pdf_file(file_path, output_dir, line_height, 
                                    output_format, convert_simplified)
        else:
            return jsonify({'error': '不支援的檔案格式'}), 400
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify({'error': result.get('error', '轉換失敗')}), 500
            
    except Exception as e:
        return jsonify({'error': f'轉換過程發生錯誤: {str(e)}'}), 500


def process_epub_file(file_path, output_dir, line_height, output_format, convert_simplified):
    """處理EPUB檔案"""
    try:
        # 初始化處理器
        epub_processor = EpubProcessor(line_height=line_height)
        
        # 載入EPUB
        if not epub_processor.load_epub(file_path):
            return {'error': '載入EPUB檔案失敗'}
        
        # 獲取書籍資訊
        book_info = epub_processor.get_book_info()
        
        if output_format == 'epub':
            # 修改EPUB並輸出
            print(f"開始修改EPUB格式，轉換簡體: {convert_simplified}")
            modify_result = epub_processor.modify_reading_direction_and_font(convert_simplified)
            print(f"修改結果: {modify_result}")

            if not modify_result:
                return {'error': '修改EPUB格式失敗'}

            output_filename = f"converted_{book_info.get('title', 'book')}.epub"
            output_path = os.path.join(output_dir, output_filename)
            print(f"準備儲存到: {output_path}")

            save_result = epub_processor.save_epub(output_path)
            print(f"儲存結果: {save_result}")

            if not save_result:
                return {'error': '儲存EPUB檔案失敗'}
            
            # 獲取轉換統計
            conversion_stats = epub_processor.get_conversion_stats()
            
            return {
                'success': True,
                'output_file': output_filename,
                'output_dir': os.path.basename(output_dir),
                'book_info': book_info,
                'conversion_stats': conversion_stats,
                'message': 'EPUB轉換完成'
            }
            
        elif output_format == 'md':
            # 提取內容並生成Markdown
            chapters = epub_processor.extract_content_for_markdown()
            
            # 處理簡繁轉換
            if convert_simplified:
                for chapter in chapters:
                    original_content = chapter['content']
                    converted_content, was_converted = text_converter.convert_html_content(original_content)
                    if was_converted:
                        chapter['content'] = converted_content
            
            # 生成Markdown
            markdown_generator = MarkdownGenerator(line_height=line_height)
            markdown_file = markdown_generator.generate_from_epub_content(
                chapters, book_info, output_dir
            )

            output_filename = os.path.basename(markdown_file)

            return {
                'success': True,
                'output_file': output_filename,
                'output_dir': os.path.basename(output_dir),
                'book_info': book_info,
                'message': 'Markdown轉換完成'
            }
            
    except Exception as e:
        return {'error': f'EPUB處理失敗: {str(e)}'}


def process_pdf_file(file_path, output_dir, line_height, output_format, convert_simplified):
    """處理PDF檔案"""
    try:
        # 初始化處理器
        pdf_processor = PdfProcessor()
        
        # 載入PDF
        if not pdf_processor.load_pdf(file_path):
            return {'error': '載入PDF檔案失敗'}
        
        # 獲取PDF資訊
        pdf_info = pdf_processor.get_pdf_info()
        
        # 提取內容
        pages_content = pdf_processor.extract_text_with_structure()
        pages_content = pdf_processor.detect_chapters(pages_content)
        
        # 處理簡繁轉換
        if convert_simplified:
            for page in pages_content:
                for paragraph in page['paragraphs']:
                    original_text = paragraph['text']
                    converted_text, was_converted = text_converter.auto_convert_if_simplified(original_text)
                    if was_converted:
                        paragraph['text'] = converted_text
        
        if output_format == 'md':
            # 生成Markdown
            markdown_generator = MarkdownGenerator(line_height=line_height)
            markdown_file = markdown_generator.generate_from_pdf_content(
                pages_content, pdf_info, output_dir
            )

            output_filename = os.path.basename(markdown_file)

            return {
                'success': True,
                'output_file': output_filename,
                'output_dir': os.path.basename(output_dir),
                'pdf_info': pdf_info,
                'message': 'PDF轉Markdown完成'
            }
        else:
            return {'error': 'PDF檔案僅支援轉換為Markdown格式'}
            
    except Exception as e:
        return {'error': f'PDF處理失敗: {str(e)}'}
    finally:
        pdf_processor.close()


@app.route('/download/<output_dir>/<filename>')
def download_file(output_dir, filename):
    """下載轉換後的檔案"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], output_dir, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': '檔案不存在'}), 404
    except Exception as e:
        return jsonify({'error': f'下載失敗: {str(e)}'}), 500


@app.route('/status')
def get_status():
    """獲取系統狀態"""
    return jsonify({
        'text_converter': text_converter.get_status(),
        'pdf_processor_available': PdfProcessor().is_available(),
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'max_file_size': '100MB'
    })


# Vercel需要這個變數
application = app

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
