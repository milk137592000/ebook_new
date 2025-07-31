"""
PDF處理模組
負責從PDF檔案中提取文字和結構
"""

import os
import re
from typing import List, Dict, Optional, Tuple

# 使用更輕量的PDF處理庫
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    print("警告：PyPDF2未安裝，PDF處理功能將不可用")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    print("警告：pdfplumber未安裝，PDF處理功能將受限")


class PdfProcessor:
    """PDF處理器"""
    
    def __init__(self):
        self.document = None
        self.file_path = None
        
    def load_pdf(self, file_path: str) -> bool:
        """
        載入PDF檔案

        Args:
            file_path: PDF檔案路徑

        Returns:
            bool: 載入是否成功
        """
        if not (PYPDF2_AVAILABLE or PDFPLUMBER_AVAILABLE):
            print("錯誤：PDF處理庫未安裝，無法處理PDF檔案")
            return False

        try:
            # 使用PyPDF2載入PDF
            if PYPDF2_AVAILABLE:
                # 直接載入PDF文件，不使用with語句
                self.document = PyPDF2.PdfReader(file_path)
                # 驗證PDF是否可讀
                _ = len(self.document.pages)

            self.file_path = file_path
            return True
        except Exception as e:
            print(f"載入PDF檔案失敗: {e}")
            return False
    
    def extract_text_with_structure(self) -> List[Dict]:
        """
        提取PDF文字並保持結構

        Returns:
            List[Dict]: 包含頁面和段落資訊的列表
        """
        if not self.file_path:
            return []

        pages_content = []

        try:
            # 使用已載入的document提取文字
            if self.document and PYPDF2_AVAILABLE:
                for page_num, page in enumerate(self.document.pages):
                    try:
                        text = page.extract_text()

                        page_content = {
                            'page_number': page_num + 1,
                            'paragraphs': []
                        }

                        # 簡單的段落分割
                        paragraphs = text.split('\n\n')
                        for para_text in paragraphs:
                            para_text = para_text.strip()
                            if para_text:
                                page_content['paragraphs'].append({
                                    'text': para_text,
                                    'font_size': 12,  # 預設字體大小
                                    'is_chapter': len(para_text) < 100 and para_text.isupper()  # 簡單的章節檢測
                                })

                        if page_content['paragraphs']:  # 只添加有內容的頁面
                            pages_content.append(page_content)
                    except Exception as e:
                        print(f"提取第{page_num + 1}頁失敗: {e}")
                        continue

        except Exception as e:
            print(f"提取PDF文字失敗: {e}")
        
        return pages_content
    
    def extract_simple_text(self) -> str:
        """
        簡單提取PDF中的所有文字
        
        Returns:
            str: 提取的文字內容
        """
        if not self.document:
            return ""
        
        try:
            full_text = ""
            for page in self.document.pages:
                text = page.extract_text()
                full_text += text + "\n\n"

            return full_text.strip()
        except Exception as e:
            print(f"提取PDF文字失敗: {e}")
            return ""
    
    def extract_with_pdfplumber(self, file_path: str) -> List[Dict]:
        """
        使用pdfplumber提取PDF內容（備用方法）
        
        Args:
            file_path: PDF檔案路徑
            
        Returns:
            List[Dict]: 頁面內容列表
        """
        if not PDFPLUMBER_AVAILABLE:
            return []
        
        pages_content = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    
                    if text:
                        # 簡單的段落分割
                        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                        
                        page_content = {
                            'page_number': page_num + 1,
                            'paragraphs': []
                        }
                        
                        for para in paragraphs:
                            # 簡單的標題檢測（全大寫或較短的行）
                            is_title = (para.isupper() and len(para) < 100) or \
                                      (len(para) < 50 and not para.endswith('.'))
                            
                            page_content['paragraphs'].append({
                                'text': para,
                                'is_title': is_title,
                                'font_size': 16 if is_title else 12
                            })
                        
                        if page_content['paragraphs']:
                            pages_content.append(page_content)
                            
        except Exception as e:
            print(f"pdfplumber提取失敗: {e}")
        
        return pages_content
    
    def detect_chapters(self, pages_content: List[Dict]) -> List[Dict]:
        """
        檢測章節結構
        
        Args:
            pages_content: 頁面內容列表
            
        Returns:
            List[Dict]: 包含章節資訊的內容
        """
        chapter_patterns = [
            r'^第[一二三四五六七八九十\d]+章',
            r'^Chapter\s+\d+',
            r'^第[一二三四五六七八九十\d]+節',
            r'^\d+\.',
            r'^[一二三四五六七八九十]+、',
        ]
        
        for page in pages_content:
            for paragraph in page['paragraphs']:
                text = paragraph['text']
                
                # 檢查是否匹配章節模式
                for pattern in chapter_patterns:
                    if re.match(pattern, text, re.IGNORECASE):
                        paragraph['is_chapter'] = True
                        paragraph['is_title'] = True
                        break
                else:
                    paragraph['is_chapter'] = False
        
        return pages_content
    
    def get_pdf_info(self) -> Dict:
        """
        獲取PDF檔案資訊
        
        Returns:
            Dict: PDF檔案資訊
        """
        if not self.document:
            return {}
        
        try:
            metadata = self.document.metadata or {}

            return {
                'title': metadata.get('/Title', 'Unknown'),
                'author': metadata.get('/Author', 'Unknown'),
                'subject': metadata.get('/Subject', ''),
                'creator': metadata.get('/Creator', ''),
                'producer': metadata.get('/Producer', ''),
                'creation_date': str(metadata.get('/CreationDate', '')),
                'modification_date': str(metadata.get('/ModDate', '')),
                'page_count': len(self.document.pages),
                'file_size': os.path.getsize(self.file_path) if self.file_path else 0
            }
        except Exception as e:
            print(f"獲取PDF資訊失敗: {e}")
            return {'page_count': len(self.document.pages) if self.document else 0}
    
    def close(self):
        """關閉PDF檔案"""
        # PyPDF2的PdfReader不需要手動關閉
        # 只需要清空引用即可
        self.document = None
        self.file_path = None
    
    def pdf_to_markdown(self, input_path: str, output_path: str) -> bool:
        """
        將PDF轉換為Markdown格式

        Args:
            input_path: 輸入PDF檔案路徑
            output_path: 輸出Markdown檔案路徑

        Returns:
            bool: 轉換是否成功
        """
        try:
            # 載入PDF
            if not self.load_pdf(input_path):
                return False

            # 提取文字內容
            if PDFPLUMBER_AVAILABLE:
                pages_content = self.extract_with_pdfplumber(input_path)
            else:
                pages_content = self.extract_text_with_structure()

            if not pages_content:
                return False

            # 轉換為Markdown
            markdown_content = self._convert_to_markdown(pages_content)

            # 儲存Markdown檔案
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            self.close()
            return True

        except Exception as e:
            print(f"PDF轉Markdown失敗: {e}")
            return False

    def _convert_to_markdown(self, pages_content: List[Dict]) -> str:
        """
        將頁面內容轉換為Markdown格式

        Args:
            pages_content: 頁面內容列表

        Returns:
            str: Markdown內容
        """
        markdown_lines = []

        # 添加標題
        markdown_lines.append("# PDF轉換文檔\n")

        for page_idx, page in enumerate(pages_content):
            # 添加頁面標題
            markdown_lines.append(f"## 第 {page_idx + 1} 頁\n")

            # 處理段落
            if 'paragraphs' in page:
                for para in page['paragraphs']:
                    text = para.get('text', '').strip()
                    if text:
                        # 檢查是否為章節標題
                        if para.get('is_chapter', False):
                            markdown_lines.append(f"### {text}\n")
                        else:
                            markdown_lines.append(f"{text}\n")
                        markdown_lines.append("")  # 空行
            elif 'text' in page:
                # 簡單文字內容
                text = page['text'].strip()
                if text:
                    markdown_lines.append(f"{text}\n")
                    markdown_lines.append("")  # 空行

        return "\n".join(markdown_lines)

    def is_available(self) -> bool:
        """
        檢查PDF處理功能是否可用

        Returns:
            bool: 是否可用
        """
        return PYPDF2_AVAILABLE or PDFPLUMBER_AVAILABLE
    
    def get_status(self) -> str:
        """
        獲取PDF處理器狀態
        
        Returns:
            str: 狀態描述
        """
        if PYPDF2_AVAILABLE and PDFPLUMBER_AVAILABLE:
            return "PDF處理器已就緒 (PyPDF2 + pdfplumber)"
        elif PYPDF2_AVAILABLE:
            return "PDF處理器已就緒 (PyPDF2)"
        elif PDFPLUMBER_AVAILABLE:
            return "PDF處理器已就緒 (pdfplumber)"
        else:
            return "PDF處理器不可用"
