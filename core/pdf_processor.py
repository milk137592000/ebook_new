"""
PDF處理模組
負責從PDF檔案中提取文字和結構
"""

import os
import re
from typing import List, Dict, Optional, Tuple

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("警告：PyMuPDF未安裝，PDF處理功能將不可用")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    print("警告：pdfplumber未安裝，PDF處理功能將受限")


class PDFProcessor:
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
        if not PYMUPDF_AVAILABLE:
            print("錯誤：PyMuPDF未安裝，無法處理PDF檔案")
            return False
        
        try:
            self.document = fitz.open(file_path)
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
        if not self.document:
            return []
        
        pages_content = []
        
        try:
            for page_num in range(len(self.document)):
                page = self.document[page_num]
                
                # 提取文字塊
                text_blocks = page.get_text("dict")
                
                page_content = {
                    'page_number': page_num + 1,
                    'paragraphs': []
                }
                
                # 處理文字塊
                for block in text_blocks.get("blocks", []):
                    if "lines" in block:
                        paragraph_text = ""
                        font_sizes = []
                        
                        for line in block["lines"]:
                            line_text = ""
                            for span in line.get("spans", []):
                                text = span.get("text", "").strip()
                                if text:
                                    line_text += text + " "
                                    font_sizes.append(span.get("size", 12))
                            
                            if line_text.strip():
                                paragraph_text += line_text.strip() + "\n"
                        
                        if paragraph_text.strip():
                            # 判斷是否為標題（基於字體大小）
                            avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 12
                            is_title = avg_font_size > 14  # 假設大於14pt的為標題
                            
                            page_content['paragraphs'].append({
                                'text': paragraph_text.strip(),
                                'is_title': is_title,
                                'font_size': avg_font_size
                            })
                
                if page_content['paragraphs']:
                    pages_content.append(page_content)
                    
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
            for page_num in range(len(self.document)):
                page = self.document[page_num]
                text = page.get_text()
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
            metadata = self.document.metadata
            
            return {
                'title': metadata.get('title', 'Unknown'),
                'author': metadata.get('author', 'Unknown'),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', ''),
                'page_count': len(self.document),
                'file_size': os.path.getsize(self.file_path) if self.file_path else 0
            }
        except Exception as e:
            print(f"獲取PDF資訊失敗: {e}")
            return {'page_count': len(self.document) if self.document else 0}
    
    def close(self):
        """關閉PDF檔案"""
        if self.document:
            self.document.close()
            self.document = None
            self.file_path = None
    
    def is_available(self) -> bool:
        """
        檢查PDF處理功能是否可用
        
        Returns:
            bool: 是否可用
        """
        return PYMUPDF_AVAILABLE or PDFPLUMBER_AVAILABLE
    
    def get_status(self) -> str:
        """
        獲取PDF處理器狀態
        
        Returns:
            str: 狀態描述
        """
        if PYMUPDF_AVAILABLE and PDFPLUMBER_AVAILABLE:
            return "PDF處理功能完全可用（PyMuPDF + pdfplumber）"
        elif PYMUPDF_AVAILABLE:
            return "PDF處理功能可用（僅PyMuPDF）"
        elif PDFPLUMBER_AVAILABLE:
            return "PDF處理功能受限（僅pdfplumber）"
        else:
            return "PDF處理功能不可用，請安裝: pip install PyMuPDF pdfplumber"
