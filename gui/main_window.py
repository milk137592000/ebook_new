"""
主視窗GUI模組
提供使用者介面功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from typing import Optional

from core.epub_processor import EpubProcessor
from core.format_converter import FormatConverter
from utils.helpers import (
    validate_epub_file, generate_output_filename, 
    ensure_directory_exists, get_file_size_mb,
    format_file_size, validate_output_path,
    truncate_text, get_format_description
)


class MainWindow:
    """主視窗類別"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.epub_processor = EpubProcessor()
        self.format_converter = FormatConverter()
        
        # 變數
        self.input_file_path = tk.StringVar()
        self.output_directory = tk.StringVar()
        self.output_format = tk.StringVar(value='epub')
        self.progress_text = tk.StringVar(value='準備就緒')
        
        # 設定預設輸出目錄為桌面
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        if os.path.exists(desktop_path):
            self.output_directory.set(desktop_path)
        
        self.setup_ui()
        self.update_format_info()
    
    def setup_ui(self):
        """設定使用者介面"""
        self.root.title('EPUB格式轉換器 - 直向轉橫向')
        self.root.geometry('600x500')
        self.root.resizable(True, True)
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置網格權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 標題
        title_label = ttk.Label(main_frame, text='EPUB格式轉換器', 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 檔案選擇區域
        self.create_file_selection_area(main_frame, 1)
        
        # 輸出設定區域
        self.create_output_settings_area(main_frame, 2)
        
        # 轉換按鈕
        self.create_conversion_area(main_frame, 3)
        
        # 進度顯示區域
        self.create_progress_area(main_frame, 4)
        
        # 狀態列
        self.create_status_area(main_frame, 5)
    
    def create_file_selection_area(self, parent, row):
        """創建檔案選擇區域"""
        # 檔案選擇框架
        file_frame = ttk.LabelFrame(parent, text='選擇EPUB檔案', padding="10")
        file_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # 檔案路徑顯示
        ttk.Label(file_frame, text='檔案:').grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.file_entry = ttk.Entry(file_frame, textvariable=self.input_file_path, 
                                   state='readonly', width=50)
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(file_frame, text='瀏覽...', 
                  command=self.browse_input_file).grid(row=0, column=2)
        
        # 檔案資訊顯示
        self.file_info_label = ttk.Label(file_frame, text='', foreground='gray')
        self.file_info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
    
    def create_output_settings_area(self, parent, row):
        """創建輸出設定區域"""
        # 輸出設定框架
        output_frame = ttk.LabelFrame(parent, text='輸出設定', padding="10")
        output_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        # 輸出格式選擇
        ttk.Label(output_frame, text='格式:').grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        format_frame = ttk.Frame(output_frame)
        format_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        formats = self.format_converter.get_supported_formats()
        for i, fmt in enumerate(formats):
            ttk.Radiobutton(format_frame, text=fmt.upper(), value=fmt,
                           variable=self.output_format,
                           command=self.update_format_info).grid(row=0, column=i, padx=(0, 10))
        
        # 格式說明
        self.format_info_label = ttk.Label(output_frame, text='', foreground='blue')
        self.format_info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # 輸出目錄選擇
        ttk.Label(output_frame, text='目錄:').grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_directory, 
                                     state='readonly', width=50)
        self.output_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(10, 0))
        
        ttk.Button(output_frame, text='瀏覽...', 
                  command=self.browse_output_directory).grid(row=2, column=2, pady=(10, 0))
    
    def create_conversion_area(self, parent, row):
        """創建轉換按鈕區域"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        self.convert_button = ttk.Button(button_frame, text='開始轉換', 
                                        command=self.start_conversion,
                                        style='Accent.TButton')
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_button = ttk.Button(button_frame, text='取消', 
                                       command=self.cancel_conversion,
                                       state='disabled')
        self.cancel_button.pack(side=tk.LEFT)
    
    def create_progress_area(self, parent, row):
        """創建進度顯示區域"""
        progress_frame = ttk.LabelFrame(parent, text='轉換進度', padding="10")
        progress_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        # 進度條
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 進度文字
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_text)
        self.progress_label.grid(row=1, column=0, sticky=tk.W)
    
    def create_status_area(self, parent, row):
        """創建狀態列"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        # Calibre狀態
        calibre_status = self.format_converter.get_calibre_status()
        self.status_label = ttk.Label(status_frame, text=calibre_status, foreground='gray')
        self.status_label.grid(row=0, column=0, sticky=tk.W)
    
    def browse_input_file(self):
        """瀏覽輸入檔案"""
        file_path = filedialog.askopenfilename(
            title='選擇EPUB檔案',
            filetypes=[('EPUB files', '*.epub'), ('All files', '*.*')]
        )
        
        if file_path:
            if validate_epub_file(file_path):
                self.input_file_path.set(file_path)
                self.update_file_info()
            else:
                messagebox.showerror('錯誤', '請選擇有效的EPUB檔案')
    
    def browse_output_directory(self):
        """瀏覽輸出目錄"""
        directory = filedialog.askdirectory(title='選擇輸出目錄')
        if directory:
            self.output_directory.set(directory)
    
    def update_file_info(self):
        """更新檔案資訊顯示"""
        file_path = self.input_file_path.get()
        if file_path and os.path.exists(file_path):
            file_size = get_file_size_mb(file_path)
            filename = os.path.basename(file_path)
            info_text = f"檔案: {truncate_text(filename, 40)} ({file_size:.1f} MB)"
            self.file_info_label.config(text=info_text)
        else:
            self.file_info_label.config(text='')
    
    def update_format_info(self):
        """更新格式資訊顯示"""
        format_type = self.output_format.get()
        description = get_format_description(format_type)
        self.format_info_label.config(text=description)
    
    def start_conversion(self):
        """開始轉換"""
        # 驗證輸入
        if not self.input_file_path.get():
            messagebox.showerror('錯誤', '請選擇EPUB檔案')
            return
        
        if not self.output_directory.get():
            messagebox.showerror('錯誤', '請選擇輸出目錄')
            return
        
        # 生成輸出檔案路徑
        output_filename = generate_output_filename(
            self.input_file_path.get(), 
            self.output_format.get()
        )
        output_path = os.path.join(self.output_directory.get(), output_filename)
        
        # 驗證輸出路徑
        is_valid, error_msg = validate_output_path(output_path)
        if not is_valid:
            messagebox.showerror('錯誤', error_msg)
            return
        
        # 確認覆寫
        if os.path.exists(output_path):
            if not messagebox.askyesno('確認', f'檔案已存在，是否覆寫？\n{output_path}'):
                return
        
        # 開始轉換
        self.set_conversion_state(True)
        
        # 在新執行緒中執行轉換
        conversion_thread = threading.Thread(
            target=self.perform_conversion,
            args=(self.input_file_path.get(), output_path),
            daemon=True
        )
        conversion_thread.start()
    
    def perform_conversion(self, input_path: str, output_path: str):
        """執行轉換（在背景執行緒中）"""
        try:
            # 載入EPUB
            self.update_progress("載入EPUB檔案...")
            if not self.epub_processor.load_epub(input_path):
                self.show_error("載入EPUB檔案失敗")
                return
            
            # 修改格式
            self.update_progress("修改閱讀方向和字型...")
            if not self.epub_processor.modify_reading_direction_and_font():
                self.show_error("修改EPUB格式失敗")
                return
            
            # 儲存修改後的EPUB
            temp_epub_path = output_path if self.output_format.get() == 'epub' else output_path + '.temp.epub'
            
            self.update_progress("儲存修改後的EPUB...")
            if not self.epub_processor.save_epub(temp_epub_path):
                self.show_error("儲存EPUB檔案失敗")
                return
            
            # 格式轉換
            if self.output_format.get() != 'epub':
                success = self.format_converter.convert_format(
                    temp_epub_path, output_path, self.output_format.get(),
                    self.update_progress
                )
                
                # 清理臨時檔案
                try:
                    os.remove(temp_epub_path)
                except:
                    pass
                
                if not success:
                    self.show_error("格式轉換失敗")
                    return
            
            # 完成
            self.show_success(f"轉換完成！\n輸出檔案: {output_path}")
            
        except Exception as e:
            self.show_error(f"轉換過程發生錯誤: {e}")
        finally:
            self.root.after(0, lambda: self.set_conversion_state(False))
    
    def cancel_conversion(self):
        """取消轉換"""
        # 這裡可以實作取消邏輯
        self.set_conversion_state(False)
        self.update_progress("已取消")
    
    def set_conversion_state(self, converting: bool):
        """設定轉換狀態"""
        if converting:
            self.convert_button.config(state='disabled')
            self.cancel_button.config(state='normal')
            self.progress_bar.start()
        else:
            self.convert_button.config(state='normal')
            self.cancel_button.config(state='disabled')
            self.progress_bar.stop()
    
    def update_progress(self, message: str):
        """更新進度訊息"""
        self.root.after(0, lambda: self.progress_text.set(message))
    
    def show_error(self, message: str):
        """顯示錯誤訊息"""
        self.root.after(0, lambda: messagebox.showerror('錯誤', message))
    
    def show_success(self, message: str):
        """顯示成功訊息"""
        self.root.after(0, lambda: messagebox.showinfo('完成', message))
    
    def run(self):
        """執行主迴圈"""
        self.root.mainloop()
