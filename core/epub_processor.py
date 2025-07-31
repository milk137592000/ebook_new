"""
EPUB處理核心模組
負責讀取、修改和儲存EPUB檔案
"""

import os
import re
import zipfile
from typing import Optional, List, Dict, Tuple
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from .text_converter import text_converter


class EpubProcessor:
    """EPUB檔案處理器"""
    
    def __init__(self, line_height: float = 1.6):
        self.book: Optional[epub.EpubBook] = None
        self.original_path: Optional[str] = None
        self.line_height = float(line_height)  # 確保是float類型
        self.conversion_stats = {
            'simplified_detected': False,
            'conversion_performed': False,
            'total_chars': 0,
            'changed_chars': 0
        }
        
    def load_epub(self, file_path: str) -> bool:
        """
        載入EPUB檔案
        
        Args:
            file_path: EPUB檔案路徑
            
        Returns:
            bool: 載入是否成功
        """
        try:
            self.book = epub.read_epub(file_path)
            self.original_path = file_path
            return True
        except Exception as e:
            print(f"載入EPUB檔案失敗: {e}")
            return False
    
    def modify_reading_direction_and_font(self, convert_simplified: bool = True) -> bool:
        """
        修改閱讀方向和字型，並可選擇進行簡繁轉換

        Args:
            convert_simplified: 是否進行簡體轉正體轉換

        Returns:
            bool: 修改是否成功
        """
        if not self.book:
            return False
            
        try:
            # 創建新的CSS樣式
            new_css = self._create_horizontal_css()
            print(f"生成的CSS長度: {len(new_css)}")

            # 添加新的CSS檔案
            css_item = epub.EpubItem(
                uid="horizontal_style",
                file_name="styles/horizontal.css",
                media_type="text/css",
                content=new_css
            )
            self.book.add_item(css_item)
            print("CSS項目已添加到書籍")

            # 修改所有HTML檔案，添加新的CSS引用和處理簡繁轉換
            self._add_css_to_html_files(css_item, convert_simplified)
            print("HTML檔案已修改")

            # 修改OPF檔案中的閱讀方向
            self._modify_page_progression()
            print("OPF檔案已修改")

            return True
        except Exception as e:
            print(f"修改EPUB失敗: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_horizontal_css(self) -> str:
        """
        創建橫向閱讀的CSS樣式
        
        Returns:
            str: CSS內容
        """
        css_content = (
            "/* 橫向閱讀樣式 */\n"
            "html, body {\n"
            f"    writing-mode: horizontal-tb !important;\n"
            f"    direction: ltr !important;\n"
            f"    text-orientation: mixed !important;\n"
            f"    line-height: {self.line_height} !important;\n"
            "}\n\n"
            "/* 字型設定 */\n"
            "* {\n"
            f"    font-family: \"微軟正黑體\", \"Microsoft JhengHei\", \"PingFang TC\", \"Helvetica Neue\", Arial, sans-serif !important;\n"
            f"    line-height: {self.line_height} !important;\n"
            "}\n\n"
            "/* 段落和文字樣式 */\n"
            "p, div, span, h1, h2, h3, h4, h5, h6 {\n"
            f"    writing-mode: horizontal-tb !important;\n"
            f"    direction: ltr !important;\n"
            f"    text-align: left !important;\n"
            f"    line-height: {self.line_height} !important;\n"
            "}\n\n"
            "/* 確保圖片和其他元素正確對齊 */\n"
            "img {\n"
            "    max-width: 100% !important;\n"
            "    height: auto !important;\n"
            "}\n\n"
            "/* 表格樣式 */\n"
            "table {\n"
            "    direction: ltr !important;\n"
            "}\n\n"
            "/* 列表樣式 */\n"
            "ul, ol {\n"
            "    direction: ltr !important;\n"
            "    text-align: left !important;\n"
            "}\n\n"
            "/* 移除可能的直向樣式 */\n"
            ".vertical, .vertical-rl, .vertical-lr {\n"
            "    writing-mode: horizontal-tb !important;\n"
            "    direction: ltr !important;\n"
            "}"
        )
        print(f"CSS生成成功，行距值: {self.line_height}")
        return css_content
    
    def _add_css_to_html_files(self, css_item: epub.EpubItem, convert_simplified: bool = True) -> None:
        """
        在所有HTML檔案中添加CSS引用並處理簡繁轉換

        Args:
            css_item: CSS項目
            convert_simplified: 是否進行簡體轉正體轉換
        """
        for item in self.book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # 解析HTML內容
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                
                # 檢查是否已經有head標籤
                if not soup.head:
                    head = soup.new_tag('head')
                    if soup.html:
                        soup.html.insert(0, head)
                    else:
                        soup.insert(0, head)
                
                # 添加CSS連結
                css_link = soup.new_tag('link', rel='stylesheet', type='text/css', href='../styles/horizontal.css')
                soup.head.append(css_link)

                # 處理簡繁轉換
                if convert_simplified:
                    try:
                        original_content = str(soup)
                        converted_content, was_converted = text_converter.convert_html_content(original_content)

                        if was_converted:
                            self.conversion_stats['simplified_detected'] = True
                            self.conversion_stats['conversion_performed'] = True

                            # 計算轉換統計
                            stats = text_converter.get_conversion_stats(original_content, converted_content)
                            self.conversion_stats['total_chars'] += stats['total_chars']
                            self.conversion_stats['changed_chars'] += stats['changed_chars']

                            soup = BeautifulSoup(converted_content, 'html.parser')
                    except Exception as e:
                        print(f"簡繁轉換處理失敗: {e}")

                # 更新內容
                try:
                    content_str = str(soup)
                    if content_str and content_str.strip():
                        item.set_content(content_str.encode('utf-8'))
                        print(f"成功更新檔案: {item.get_name()}")
                    else:
                        print(f"警告：檔案內容為空，跳過更新: {item.get_name()}")
                except Exception as e:
                    print(f"更新內容失敗: {e}, 檔案: {item.get_name()}")
                    # 如果更新失敗，保持原始內容
                    try:
                        original_content = item.get_content()
                        if original_content:
                            item.set_content(original_content)
                            print(f"恢復原始內容: {item.get_name()}")
                    except:
                        pass
    
    def _modify_page_progression(self) -> None:
        """修改頁面進展方向"""
        # 這個功能需要直接修改OPF檔案
        # 由於ebooklib的限制，我們可能需要在儲存後手動修改
        pass
    
    def save_epub(self, output_path: str) -> bool:
        """
        儲存修改後的EPUB檔案
        
        Args:
            output_path: 輸出檔案路徑
            
        Returns:
            bool: 儲存是否成功
        """
        if not self.book:
            return False
            
        try:
            # 在儲存前驗證所有項目的內容
            self._validate_book_content()

            # 嘗試正常儲存
            try:
                epub.write_epub(output_path, self.book)
            except Exception as e:
                print(f"正常儲存失敗，嘗試禁用NCX: {e}")
                # 如果失敗，嘗試禁用NCX
                epub.write_epub(output_path, self.book, {'ignore_ncx': True})

            # 後處理：修改OPF檔案中的page-progression-direction
            self._post_process_opf(output_path)

            return True
        except Exception as e:
            print(f"儲存EPUB檔案失敗: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _validate_book_content(self) -> None:
        """驗證書籍內容，確保沒有None值"""
        if not self.book:
            return

        print("驗證書籍內容...")

        # 驗證所有項目的內容和屬性
        for item in self.book.get_items():
            try:
                # 檢查並修復uid
                if not hasattr(item, 'uid') or item.uid is None:
                    # 生成一個安全的uid
                    safe_name = item.get_name().replace('.', '_').replace('/', '_')
                    item.uid = f"item_{safe_name}_{id(item)}"
                    print(f"修復uid: {item.get_name()} -> {item.uid}")

                # 檢查並修復file_name
                if not hasattr(item, 'file_name') or item.file_name is None:
                    item.file_name = item.get_name()
                    print(f"修復file_name: {item.get_name()}")

                # 檢查內容
                content = item.get_content()
                if content is None:
                    print(f"警告：檔案內容為None: {item.get_name()}")
                    # 設置一個最小的有效內容
                    if item.get_type() == ebooklib.ITEM_DOCUMENT:
                        item.set_content(b'<html><head><title>Empty</title></head><body></body></html>')
                    else:
                        item.set_content(b'')
                elif isinstance(content, str):
                    # 如果是字符串，轉換為字節
                    item.set_content(content.encode('utf-8'))
                elif not isinstance(content, bytes):
                    print(f"警告：檔案內容類型異常: {item.get_name()}, 類型: {type(content)}")
                    item.set_content(str(content).encode('utf-8'))

            except Exception as e:
                print(f"驗證檔案失敗: {item.get_name()}, 錯誤: {e}")
                # 設置一個安全的預設內容
                try:
                    item.set_content(b'')
                    if not hasattr(item, 'uid') or item.uid is None:
                        item.uid = f"item_error_{id(item)}"
                except:
                    pass

        # 驗證目錄結構
        self._validate_toc()

        print("書籍內容驗證完成")

    def _validate_toc(self) -> None:
        """驗證並修復目錄結構"""
        if not self.book.toc:
            print("目錄為空，跳過目錄驗證")
            return

        def fix_toc_item(item, index=0):
            """修復目錄項目"""
            if hasattr(item, 'uid') and item.uid is None:
                item.uid = f"toc_item_{index}_{id(item)}"
                print(f"修復目錄項目uid: {item.uid}")

            if hasattr(item, '__iter__') and not isinstance(item, str):
                # 如果是列表或元組，遞歸處理
                for i, sub_item in enumerate(item):
                    fix_toc_item(sub_item, i)

        try:
            if isinstance(self.book.toc, (list, tuple)):
                for i, item in enumerate(self.book.toc):
                    fix_toc_item(item, i)
            else:
                fix_toc_item(self.book.toc)
        except Exception as e:
            print(f"修復目錄失敗: {e}")
            # 如果目錄有問題，清空它
            self.book.toc = []

    def _post_process_opf(self, epub_path: str) -> None:
        """
        後處理OPF檔案，確保page-progression-direction正確
        
        Args:
            epub_path: EPUB檔案路徑
        """
        try:
            # 讀取EPUB檔案
            with zipfile.ZipFile(epub_path, 'r') as zip_read:
                # 找到OPF檔案
                container_content = zip_read.read('META-INF/container.xml').decode('utf-8')
                soup = BeautifulSoup(container_content, 'xml')
                opf_path = soup.find('rootfile')['full-path']
                
                # 讀取OPF內容
                opf_content = zip_read.read(opf_path).decode('utf-8')
                
                # 修改page-progression-direction
                opf_content = re.sub(
                    r'page-progression-direction="[^"]*"',
                    'page-progression-direction="ltr"',
                    opf_content
                )
                
                # 如果沒有找到，則添加
                if 'page-progression-direction' not in opf_content:
                    opf_content = re.sub(
                        r'(<spine[^>]*)(>)',
                        r'\1 page-progression-direction="ltr"\2',
                        opf_content
                    )
                
                # 重新打包EPUB
                temp_files = {}
                for file_info in zip_read.infolist():
                    if file_info.filename == opf_path:
                        temp_files[file_info.filename] = opf_content.encode('utf-8')
                    else:
                        temp_files[file_info.filename] = zip_read.read(file_info.filename)
            
            # 重寫EPUB檔案
            with zipfile.ZipFile(epub_path, 'w', zipfile.ZIP_DEFLATED) as zip_write:
                for filename, content in temp_files.items():
                    zip_write.writestr(filename, content)
                    
        except Exception as e:
            print(f"後處理OPF檔案失敗: {e}")
    
    def extract_content_for_markdown(self) -> List[Dict]:
        """
        提取EPUB內容用於Markdown轉換

        Returns:
            List[Dict]: 章節內容列表
        """
        if not self.book:
            return []

        chapters = []

        try:
            for item in self.book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    # 解析HTML內容
                    soup = BeautifulSoup(item.get_content(), 'html.parser')

                    # 提取標題
                    title_tag = soup.find(['h1', 'h2', 'title'])
                    title = title_tag.get_text().strip() if title_tag else item.get_name()

                    # 提取內容
                    content = str(soup)

                    chapters.append({
                        'title': title,
                        'content': content,
                        'file_name': item.get_name()
                    })

        except Exception as e:
            print(f"提取EPUB內容失敗: {e}")

        return chapters

    def get_conversion_stats(self) -> Dict:
        """
        獲取簡繁轉換統計資訊

        Returns:
            Dict: 轉換統計資訊
        """
        stats = self.conversion_stats.copy()
        if stats['total_chars'] > 0:
            stats['change_rate'] = round(
                (stats['changed_chars'] / stats['total_chars']) * 100, 2
            )
        else:
            stats['change_rate'] = 0.0

        return stats

    def get_book_info(self) -> dict:
        """
        獲取書籍資訊
        
        Returns:
            dict: 書籍資訊
        """
        if not self.book:
            return {}
            
        return {
            'title': self.book.get_metadata('DC', 'title')[0][0] if self.book.get_metadata('DC', 'title') else 'Unknown',
            'author': self.book.get_metadata('DC', 'creator')[0][0] if self.book.get_metadata('DC', 'creator') else 'Unknown',
            'language': self.book.get_metadata('DC', 'language')[0][0] if self.book.get_metadata('DC', 'language') else 'Unknown'
        }
