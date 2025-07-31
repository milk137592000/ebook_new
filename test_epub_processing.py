#!/usr/bin/env python3
"""
測試EPUB處理功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.epub_processor import EpubProcessor

def test_epub_processing():
    """測試EPUB處理功能"""
    
    # 檢查測試檔案是否存在
    test_files = ['test_vertical_book.epub', 'test_simplified_chinese_book.epub']
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n=== 測試檔案: {test_file} ===")
            
            # 創建處理器
            processor = EpubProcessor(line_height=1.6)
            
            # 載入EPUB
            print("1. 載入EPUB...")
            if processor.load_epub(test_file):
                print("✅ EPUB載入成功")
                
                # 獲取書籍資訊
                book_info = processor.get_book_info()
                print(f"書籍標題: {book_info.get('title', 'Unknown')}")
                print(f"作者: {book_info.get('author', 'Unknown')}")
                
                # 修改格式
                print("2. 修改閱讀方向和字型...")
                if processor.modify_reading_direction_and_font(convert_simplified=True):
                    print("✅ 格式修改成功")
                    
                    # 獲取轉換統計
                    stats = processor.get_conversion_stats()
                    print(f"簡繁轉換統計: {stats}")
                    
                    # 儲存修改後的檔案
                    output_file = f"converted_{test_file}"
                    print(f"3. 儲存為: {output_file}")
                    if processor.save_epub(output_file):
                        print("✅ 檔案儲存成功")
                    else:
                        print("❌ 檔案儲存失敗")
                else:
                    print("❌ 格式修改失敗")
            else:
                print("❌ EPUB載入失敗")
        else:
            print(f"⚠️  測試檔案不存在: {test_file}")

if __name__ == "__main__":
    test_epub_processing()
