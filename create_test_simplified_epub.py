#!/usr/bin/env python3
"""
創建包含簡體中文的測試EPUB檔案
"""

import os
from ebooklib import epub

def create_simplified_chinese_epub():
    """創建一個包含簡體中文的測試EPUB檔案"""
    
    # 創建書籍
    book = epub.EpubBook()
    
    # 設定書籍資訊
    book.set_identifier('test-simplified-epub-001')
    book.set_title('测试书籍 - 简体中文版')
    book.set_language('zh-CN')
    book.add_author('测试作者')
    
    # 創建章節
    c1 = epub.EpubHtml(title='第一章', file_name='chap_01.xhtml', lang='zh-CN')
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
        <h1>第一章：测试章节</h1>
        <p>这是一个测试用的EPUB文件，目前使用直向阅读模式（由右至左，由上到下）。</p>
        <p>本应用程序将会把这个格式转换为横向阅读模式（由左至右，由上到下），并更改字体为微软正黑体。</p>
        <p>这段文字包含了简体中文字符，用来测试简繁转换的效果。</p>
        <p>转换后，在Kindle上阅读时，左侧应该是上一页，右侧应该是下一页。</p>
        <p>常见的简体字：国家、发展、会议、说话、来到、对于、开始、关于、门户、问题。</p>
        <p>更多简体字：时间、实现、学习、业务、产品、经济、社会、党政、政府、军队。</p>
    </body>
    </html>
    '''
    
    c2 = epub.EpubHtml(title='第二章', file_name='chap_02.xhtml', lang='zh-CN')
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
        <h1>第二章：更多测试内容</h1>
        <p>这是第二章的内容，同样使用直向阅读模式。</p>
        <p>转换后，这些文字应该变成横向排列，并使用微软正黑体字体。</p>
        <p>测试各种标点符号：，。！？；：「」『』（）【】</p>
        <p>测试数字和英文：123 ABC abc</p>
        <p>简体字测试：组织、级别、类型、种类、样式、方法、规则、制度、系统、结构。</p>
        <p>建设、计划、项目、标准、确定、决议、讨论、证明、显示、表达。</p>
        <p>述说、讲话、语言、词汇、字符、号码、数量、价值、费用、成本。</p>
        <p>利益、效果、应该、须要、需求、供给、提供、贡献、献身、服务。</p>
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
    output_path = 'test_simplified_chinese_book.epub'
    epub.write_epub(output_path, book, {})
    
    print(f"簡體中文測試EPUB檔案已創建: {output_path}")
    return output_path

if __name__ == "__main__":
    create_simplified_chinese_epub()
