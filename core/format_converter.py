"""
格式轉換模組
負責將EPUB轉換為其他格式（MOBI、PDF）
"""

import os
import subprocess
import shutil
from typing import Optional, Callable


class FormatConverter:
    """格式轉換器"""
    
    def __init__(self):
        self.calibre_available = self._check_calibre()
    
    def _check_calibre(self) -> bool:
        """
        檢查Calibre是否可用
        
        Returns:
            bool: Calibre是否可用
        """
        try:
            result = subprocess.run(['ebook-convert', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def convert_to_mobi(self, epub_path: str, output_path: str, 
                       progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        轉換EPUB為MOBI格式
        
        Args:
            epub_path: 輸入EPUB檔案路徑
            output_path: 輸出MOBI檔案路徑
            progress_callback: 進度回調函數
            
        Returns:
            bool: 轉換是否成功
        """
        if not self.calibre_available:
            if progress_callback:
                progress_callback("錯誤：未找到Calibre，請先安裝Calibre")
            return False
        
        try:
            if progress_callback:
                progress_callback("開始轉換為MOBI格式...")
            
            # 構建轉換命令
            cmd = [
                'ebook-convert',
                epub_path,
                output_path,
                '--output-profile=kindle',
                '--mobi-file-type=new',
                '--no-inline-toc',
                '--max-toc-links=0',
                '--disable-font-rescaling'
            ]
            
            # 執行轉換
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, text=True)
            
            # 監控進度
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output and progress_callback:
                    progress_callback(f"轉換中: {output.strip()}")
            
            # 檢查結果
            return_code = process.poll()
            if return_code == 0:
                if progress_callback:
                    progress_callback("MOBI轉換完成！")
                return True
            else:
                error_output = process.stderr.read()
                if progress_callback:
                    progress_callback(f"MOBI轉換失敗: {error_output}")
                return False
                
        except Exception as e:
            if progress_callback:
                progress_callback(f"MOBI轉換錯誤: {e}")
            return False
    
    def convert_to_pdf(self, epub_path: str, output_path: str,
                      progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        轉換EPUB為PDF格式
        
        Args:
            epub_path: 輸入EPUB檔案路徑
            output_path: 輸出PDF檔案路徑
            progress_callback: 進度回調函數
            
        Returns:
            bool: 轉換是否成功
        """
        if not self.calibre_available:
            if progress_callback:
                progress_callback("錯誤：未找到Calibre，請先安裝Calibre")
            return False
        
        try:
            if progress_callback:
                progress_callback("開始轉換為PDF格式...")
            
            # 構建轉換命令
            cmd = [
                'ebook-convert',
                epub_path,
                output_path,
                '--pdf-page-numbers',
                '--pdf-add-toc',
                '--paper-size=a4',
                '--pdf-default-font-size=12',
                '--pdf-mono-font-size=10',
                '--margin-left=36',
                '--margin-right=36',
                '--margin-top=36',
                '--margin-bottom=36'
            ]
            
            # 執行轉換
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, text=True)
            
            # 監控進度
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output and progress_callback:
                    progress_callback(f"轉換中: {output.strip()}")
            
            # 檢查結果
            return_code = process.poll()
            if return_code == 0:
                if progress_callback:
                    progress_callback("PDF轉換完成！")
                return True
            else:
                error_output = process.stderr.read()
                if progress_callback:
                    progress_callback(f"PDF轉換失敗: {error_output}")
                return False
                
        except Exception as e:
            if progress_callback:
                progress_callback(f"PDF轉換錯誤: {e}")
            return False
    
    def convert_format(self, epub_path: str, output_path: str, format_type: str,
                      progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        通用格式轉換方法
        
        Args:
            epub_path: 輸入EPUB檔案路徑
            output_path: 輸出檔案路徑
            format_type: 輸出格式 ('epub', 'mobi', 'pdf')
            progress_callback: 進度回調函數
            
        Returns:
            bool: 轉換是否成功
        """
        format_type = format_type.lower()
        
        if format_type == 'epub':
            # 直接複製檔案
            try:
                if progress_callback:
                    progress_callback("複製EPUB檔案...")
                shutil.copy2(epub_path, output_path)
                if progress_callback:
                    progress_callback("EPUB檔案複製完成！")
                return True
            except Exception as e:
                if progress_callback:
                    progress_callback(f"複製EPUB檔案失敗: {e}")
                return False
        
        elif format_type == 'mobi':
            return self.convert_to_mobi(epub_path, output_path, progress_callback)
        
        elif format_type == 'pdf':
            return self.convert_to_pdf(epub_path, output_path, progress_callback)
        
        else:
            if progress_callback:
                progress_callback(f"不支援的格式: {format_type}")
            return False
    
    def get_supported_formats(self) -> list:
        """
        獲取支援的輸出格式
        
        Returns:
            list: 支援的格式列表
        """
        formats = ['epub']
        
        if self.calibre_available:
            formats.extend(['mobi', 'pdf'])
        
        return formats
    
    def get_calibre_status(self) -> str:
        """
        獲取Calibre狀態資訊
        
        Returns:
            str: 狀態資訊
        """
        if self.calibre_available:
            try:
                result = subprocess.run(['ebook-convert', '--version'], 
                                      capture_output=True, text=True, timeout=10)
                version_info = result.stdout.strip().split('\n')[0]
                return f"Calibre可用: {version_info}"
            except:
                return "Calibre可用但無法獲取版本資訊"
        else:
            return "Calibre未安裝或不可用"
