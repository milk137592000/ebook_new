#!/usr/bin/env python3
"""
EPUB格式轉換器主程式
將直向閱讀的EPUB轉換為橫向閱讀，並更改字型為微軟正黑體
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加專案根目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gui.main_window import MainWindow
except ImportError as e:
    print(f"導入模組失敗: {e}")
    print("請確保已安裝所有必要的依賴套件:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def check_dependencies():
    """檢查必要的依賴套件"""
    missing_packages = []
    
    try:
        import ebooklib
    except ImportError:
        missing_packages.append('ebooklib')
    
    try:
        import bs4
    except ImportError:
        missing_packages.append('beautifulsoup4')
    
    try:
        import lxml
    except ImportError:
        missing_packages.append('lxml')
    
    if missing_packages:
        error_msg = f"缺少必要的套件: {', '.join(missing_packages)}\n"
        error_msg += "請執行以下命令安裝:\n"
        error_msg += f"pip install {' '.join(missing_packages)}"
        
        # 如果GUI可用，顯示錯誤對話框
        try:
            root = tk.Tk()
            root.withdraw()  # 隱藏主視窗
            messagebox.showerror("缺少依賴套件", error_msg)
            root.destroy()
        except:
            print(error_msg)
        
        return False
    
    return True


def main():
    """主函數"""
    print("EPUB格式轉換器啟動中...")
    
    # 檢查依賴套件
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # 創建並執行主視窗
        app = MainWindow()
        print("GUI介面已啟動")
        app.run()
        
    except KeyboardInterrupt:
        print("\n程式被使用者中斷")
        sys.exit(0)
        
    except Exception as e:
        error_msg = f"程式執行錯誤: {e}"
        print(error_msg)
        
        # 嘗試顯示錯誤對話框
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("程式錯誤", error_msg)
            root.destroy()
        except:
            pass
        
        sys.exit(1)


if __name__ == "__main__":
    main()
