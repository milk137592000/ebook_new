#!/usr/bin/env python3
"""
創建測試用的EPUB檔案
"""

import os
from ebooklib import epub

def create_test_epub():
    """創建一個簡單的測試EPUB檔案"""
    
    # 創建書籍
    book = epub.EpubBook()
    
    # 設定書籍資訊
    book.set_identifier('test-epub-001')
    book.set_title('測試書籍 - 直向閱讀')
    book.set_language('zh-TW')
    book.add_author('測試作者')
    
    # 創建章節
    c1 = epub.EpubHtml(title='第一章', file_name='chap_01.xhtml', lang='zh-TW')
    c1.content = '''
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title>第一章</title>
        <style>
            body {
                writing-mode: vertical-rl;
                direction: rtl;
                font-family: serif;
            }
            h1 {
                writing-mode: vertical-rl;
                direction: rtl;
            }
            p {
                writing-mode: vertical-rl;
                direction: rtl;
                text-align: right;
            }
        </style>
    </head>
    <body>
        <h1>第一章：測試章節</h1>
        <p>這是一個測試用的EPUB檔案，目前使用直向閱讀模式（由右至左，由上到下）。</p>
        <p>本應用程式將會把這個格式轉換為橫向閱讀模式（由左至右，由上到下），並更改字型為微軟正黑體。</p>
        <p>這段文字包含了中文字符，用來測試字型轉換的效果。</p>
        <p>轉換後，在Kindle上閱讀時，左側應該是上一頁，右側應該是下一頁。</p>
    </body>
    </html>
    '''
    
    c2 = epub.EpubHtml(title='第二章', file_name='chap_02.xhtml', lang='zh-TW')
    c2.content = '''
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title>第二章</title>
        <style>
            body {
                writing-mode: vertical-rl;
                direction: rtl;
                font-family: serif;
            }
        </style>
    </head>
    <body>
        <h1>第二章：更多測試內容</h1>
        <p>這是第二章的內容，同樣使用直向閱讀模式。</p>
        <p>轉換後，這些文字應該變成橫向排列，並使用微軟正黑體字型。</p>
        <p>測試各種標點符號：，。！？；：「」『』（）【】</p>
        <p>測試數字和英文：123 ABC abc</p>
    </body>
    </html>
    '''
    
    # 添加章節到書籍
    book.add_item(c1)
    book.add_item(c2)
    
    # 創建目錄
    book.toc = (epub.Link("chap_01.xhtml", "第一章", "intro"),
                epub.Link("chap_02.xhtml", "第二章", "c2"))
    
    # 添加導航檔案
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # 設定spine（閱讀順序）
    book.spine = ['nav', c1, c2]
    
    # 儲存EPUB檔案
    output_path = 'test_vertical_book.epub'
    epub.write_epub(output_path, book, {})
    
    print(f"測試EPUB檔案已創建: {output_path}")
    return output_path

if __name__ == "__main__":
    create_test_epub()
