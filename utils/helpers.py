"""
輔助函數模組
提供各種實用的輔助功能
"""

import os
import re
from typing import Optional, Tuple


def validate_epub_file(file_path: str) -> bool:
    """
    驗證是否為有效的EPUB檔案
    
    Args:
        file_path: 檔案路徑
        
    Returns:
        bool: 是否為有效的EPUB檔案
    """
    if not os.path.exists(file_path):
        return False
    
    if not file_path.lower().endswith('.epub'):
        return False
    
    # 可以添加更多驗證邏輯，如檢查ZIP結構等
    return True


def get_safe_filename(filename: str) -> str:
    """
    獲取安全的檔案名稱（移除特殊字符）
    
    Args:
        filename: 原始檔案名稱
        
    Returns:
        str: 安全的檔案名稱
    """
    # 移除或替換不安全的字符
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # 移除多餘的空格和點
    safe_name = re.sub(r'\s+', ' ', safe_name).strip()
    safe_name = safe_name.strip('.')
    
    # 確保不為空
    if not safe_name:
        safe_name = 'converted_book'
    
    return safe_name


def generate_output_filename(input_path: str, output_format: str, suffix: str = '_horizontal') -> str:
    """
    生成輸出檔案名稱
    
    Args:
        input_path: 輸入檔案路徑
        output_format: 輸出格式
        suffix: 檔案名稱後綴
        
    Returns:
        str: 輸出檔案名稱
    """
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    safe_name = get_safe_filename(base_name)
    
    return f"{safe_name}{suffix}.{output_format.lower()}"


def ensure_directory_exists(directory_path: str) -> bool:
    """
    確保目錄存在，如果不存在則創建
    
    Args:
        directory_path: 目錄路徑
        
    Returns:
        bool: 操作是否成功
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception:
        return False


def get_file_size_mb(file_path: str) -> float:
    """
    獲取檔案大小（MB）
    
    Args:
        file_path: 檔案路徑
        
    Returns:
        float: 檔案大小（MB）
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0.0


def format_file_size(size_bytes: int) -> str:
    """
    格式化檔案大小顯示
    
    Args:
        size_bytes: 檔案大小（位元組）
        
    Returns:
        str: 格式化的檔案大小
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def validate_output_path(output_path: str) -> Tuple[bool, str]:
    """
    驗證輸出路徑是否有效
    
    Args:
        output_path: 輸出路徑
        
    Returns:
        Tuple[bool, str]: (是否有效, 錯誤訊息)
    """
    try:
        # 檢查目錄是否存在
        directory = os.path.dirname(output_path)
        if directory and not os.path.exists(directory):
            return False, f"目錄不存在: {directory}"
        
        # 檢查是否有寫入權限
        if directory:
            if not os.access(directory, os.W_OK):
                return False, f"沒有寫入權限: {directory}"
        
        # 檢查檔案是否已存在
        if os.path.exists(output_path):
            if not os.access(output_path, os.W_OK):
                return False, f"檔案存在但無法覆寫: {output_path}"
        
        return True, ""
        
    except Exception as e:
        return False, f"路徑驗證錯誤: {e}"


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    截斷文字並添加省略號
    
    Args:
        text: 原始文字
        max_length: 最大長度
        
    Returns:
        str: 截斷後的文字
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def get_format_description(format_type: str) -> str:
    """
    獲取格式描述
    
    Args:
        format_type: 格式類型
        
    Returns:
        str: 格式描述
    """
    descriptions = {
        'epub': 'EPUB - 標準電子書格式，支援大多數閱讀器',
        'mobi': 'MOBI - Amazon Kindle專用格式',
        'pdf': 'PDF - 便攜式文件格式，保持固定排版'
    }
    
    return descriptions.get(format_type.lower(), f'{format_type.upper()} - 未知格式')


def is_valid_format(format_type: str) -> bool:
    """
    檢查是否為有效的輸出格式
    
    Args:
        format_type: 格式類型
        
    Returns:
        bool: 是否為有效格式
    """
    valid_formats = ['epub', 'mobi', 'pdf']
    return format_type.lower() in valid_formats
