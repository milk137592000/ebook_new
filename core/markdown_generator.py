"""
Markdown生成器
負責生成適合Obsidian的階層化Markdown格式
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import quote


class MarkdownGenerator:
    """Markdown生成器"""
    
    def __init__(self, line_height: float = 1.6):
        self.line_height = line_height
        self.chapter_counter = 0
        
    def generate_from_epub_content(self, book_content: List[Dict],
                                 book_info: Dict, output_dir: str) -> str:
        """
        從EPUB內容生成單一Markdown檔案

        Args:
            book_content: EPUB章節內容列表
            book_info: 書籍資訊
            output_dir: 輸出目錄

        Returns:
            str: 生成的檔案路徑
        """
        # 創建輸出目錄
        os.makedirs(output_dir, exist_ok=True)

        # 生成單一完整Markdown檔案
        return self._generate_complete_epub_file(book_content, book_info, output_dir)
    
    def generate_from_pdf_content(self, pages_content: List[Dict],
                                pdf_info: Dict, output_dir: str) -> str:
        """
        從PDF內容生成單一Markdown檔案

        Args:
            pages_content: PDF頁面內容列表
            pdf_info: PDF檔案資訊
            output_dir: 輸出目錄

        Returns:
            str: 生成的檔案路徑
        """
        # 創建輸出目錄
        os.makedirs(output_dir, exist_ok=True)

        # 合併所有頁面內容並檢測章節
        all_content = self._merge_pdf_pages(pages_content)
        chapters = self._detect_pdf_chapters(all_content)

        # 生成單一完整Markdown檔案
        return self._generate_complete_pdf_file(chapters, pdf_info, output_dir)

    def _generate_complete_epub_file(self, chapters: List[Dict], book_info: Dict,
                                   output_dir: str) -> str:
        """生成完整的EPUB Markdown檔案"""
        title = book_info.get('title', 'Unknown Book')
        safe_title = self._sanitize_filename(title)
        output_path = os.path.join(output_dir, f"{safe_title}.md")

        content = f"""# {title}

## 書籍資訊

- **作者**: {book_info.get('author', 'Unknown')}
- **語言**: {book_info.get('language', 'Unknown')}
- **轉換時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **行距**: {self.line_height}

---

<div style="line-height: {self.line_height};">

"""

        # 添加所有章節內容
        for i, chapter in enumerate(chapters):
            chapter_title = chapter.get('title', f'Chapter {i + 1}')
            chapter_content = chapter.get('content', '')

            if chapter_content.strip():
                # 清理HTML內容並轉換為Markdown
                markdown_content = self._html_to_markdown(chapter_content)

                content += f"""
## {chapter_title}

{markdown_content}

---

"""

        content += """
</div>

*本檔案由EPUB轉換器自動生成*
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_path

    def _generate_complete_pdf_file(self, chapters: List[Dict], pdf_info: Dict,
                                  output_dir: str) -> str:
        """生成完整的PDF Markdown檔案"""
        title = pdf_info.get('title', 'PDF Document')
        if title == 'Unknown' or not title.strip():
            title = 'PDF Document'

        safe_title = self._sanitize_filename(title)
        output_path = os.path.join(output_dir, f"{safe_title}.md")

        content = f"""# {title}

## 文件資訊

- **作者**: {pdf_info.get('author', 'Unknown')}
- **主題**: {pdf_info.get('subject', 'N/A')}
- **頁數**: {pdf_info.get('page_count', 'Unknown')}
- **轉換時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **行距**: {self.line_height}

---

<div style="line-height: {self.line_height};">

"""

        # 添加所有章節內容
        for i, chapter in enumerate(chapters):
            chapter_title = chapter.get('title', f'Section {i + 1}')
            chapter_content = chapter.get('content', '')

            if chapter_content.strip():
                content += f"""
## {chapter_title}

{chapter_content}

---

"""

        content += """
</div>

*本檔案由PDF轉換器自動生成*
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_path

    def _generate_index_file(self, book_info: Dict, chapters: List[Dict],
                           output_dir: str) -> str:
        """生成EPUB主索引檔案"""
        title = book_info.get('title', 'Unknown Book')
        safe_title = self._sanitize_filename(title)
        index_path = os.path.join(output_dir, f"{safe_title}.md")
        
        content = f"""# {title}

## 書籍資訊

- **作者**: {book_info.get('author', 'Unknown')}
- **語言**: {book_info.get('language', 'Unknown')}
- **轉換時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **行距**: {self.line_height}

## 目錄

"""
        
        # 添加章節連結
        for i, chapter in enumerate(chapters):
            chapter_title = chapter.get('title', f'Chapter {i + 1}')
            chapter_filename = self._sanitize_filename(f"{i+1:02d}_{chapter_title}")
            content += f"- [[{chapter_filename}|{chapter_title}]]\n"
        
        content += f"""

---

*本檔案由EPUB轉換器自動生成*

<div style="line-height: {self.line_height};">

<!-- 內容區域 -->

</div>
"""
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return index_path
    
    def _generate_chapter_file(self, chapter: Dict, chapter_num: int, 
                             output_dir: str) -> Optional[str]:
        """生成EPUB章節檔案"""
        title = chapter.get('title', f'Chapter {chapter_num}')
        content = chapter.get('content', '')
        
        if not content.strip():
            return None
        
        safe_title = self._sanitize_filename(f"{chapter_num:02d}_{title}")
        chapter_path = os.path.join(output_dir, f"{safe_title}.md")
        
        # 清理HTML內容並轉換為Markdown
        markdown_content = self._html_to_markdown(content)
        
        file_content = f"""# {title}

<div style="line-height: {self.line_height};">

{markdown_content}

</div>

---

[[{self._sanitize_filename('index')}|返回目錄]]
"""
        
        with open(chapter_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        return chapter_path
    
    def _generate_pdf_index_file(self, pdf_info: Dict, chapters: List[Dict], 
                               output_dir: str) -> str:
        """生成PDF主索引檔案"""
        title = pdf_info.get('title', 'PDF Document')
        if title == 'Unknown' or not title.strip():
            title = 'PDF Document'
        
        safe_title = self._sanitize_filename(title)
        index_path = os.path.join(output_dir, f"{safe_title}.md")
        
        content = f"""# {title}

## 文件資訊

- **作者**: {pdf_info.get('author', 'Unknown')}
- **主題**: {pdf_info.get('subject', 'N/A')}
- **頁數**: {pdf_info.get('page_count', 'Unknown')}
- **轉換時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **行距**: {self.line_height}

## 目錄

"""
        
        # 添加章節連結
        for i, chapter in enumerate(chapters):
            chapter_title = chapter.get('title', f'Section {i + 1}')
            chapter_filename = self._sanitize_filename(f"{i+1:02d}_{chapter_title}")
            content += f"- [[{chapter_filename}|{chapter_title}]]\n"
        
        content += f"""

---

*本檔案由PDF轉換器自動生成*

<div style="line-height: {self.line_height};">

<!-- 內容區域 -->

</div>
"""
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return index_path
    
    def _generate_pdf_chapter_file(self, chapter: Dict, chapter_num: int, 
                                 output_dir: str) -> Optional[str]:
        """生成PDF章節檔案"""
        title = chapter.get('title', f'Section {chapter_num}')
        content = chapter.get('content', '')
        
        if not content.strip():
            return None
        
        safe_title = self._sanitize_filename(f"{chapter_num:02d}_{title}")
        chapter_path = os.path.join(output_dir, f"{safe_title}.md")
        
        file_content = f"""# {title}

<div style="line-height: {self.line_height};">

{content}

</div>

---

[[{self._sanitize_filename('index')}|返回目錄]]
"""
        
        with open(chapter_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        return chapter_path
    
    def _merge_pdf_pages(self, pages_content: List[Dict]) -> List[Dict]:
        """合併PDF頁面內容"""
        all_paragraphs = []
        
        for page in pages_content:
            for paragraph in page['paragraphs']:
                all_paragraphs.append(paragraph)
        
        return all_paragraphs
    
    def _detect_pdf_chapters(self, paragraphs: List[Dict]) -> List[Dict]:
        """檢測PDF章節"""
        chapters = []
        current_chapter = None
        
        for paragraph in paragraphs:
            if paragraph.get('is_title', False) or paragraph.get('is_chapter', False):
                # 開始新章節
                if current_chapter:
                    chapters.append(current_chapter)
                
                current_chapter = {
                    'title': paragraph['text'][:50] + ('...' if len(paragraph['text']) > 50 else ''),
                    'content': paragraph['text'] + '\n\n'
                }
            else:
                # 添加到當前章節
                if current_chapter:
                    current_chapter['content'] += paragraph['text'] + '\n\n'
                else:
                    # 如果還沒有章節，創建第一個章節
                    current_chapter = {
                        'title': 'Introduction',
                        'content': paragraph['text'] + '\n\n'
                    }
        
        # 添加最後一個章節
        if current_chapter:
            chapters.append(current_chapter)
        
        return chapters
    
    def _html_to_markdown(self, html_content: str) -> str:
        """將HTML內容轉換為Markdown"""
        # 簡單的HTML到Markdown轉換
        content = html_content
        
        # 移除HTML標籤但保留內容
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        
        # 轉換標題
        content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', content)
        content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', content)
        content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', content)
        content = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', content)
        
        # 轉換段落
        content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', content)
        
        # 轉換強調
        content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', content)
        content = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', content)
        content = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', content)
        content = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', content)
        
        # 移除其他HTML標籤
        content = re.sub(r'<[^>]+>', '', content)
        
        # 清理多餘的空行
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        return content.strip()
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理檔案名稱"""
        # 移除或替換不安全的字符
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        safe_name = re.sub(r'\s+', '_', safe_name)
        safe_name = safe_name.strip('._')
        
        # 限制長度
        if len(safe_name) > 50:
            safe_name = safe_name[:50]
        
        return safe_name or 'untitled'
