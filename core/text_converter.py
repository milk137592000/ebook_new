"""
文字轉換模組
負責簡體轉正體中文轉換
"""

import re
from typing import Optional

try:
    import opencc
    OPENCC_AVAILABLE = True
except ImportError:
    OPENCC_AVAILABLE = False
    print("警告：OpenCC未安裝，簡繁轉換功能將不可用")


class TextConverter:
    """文字轉換器"""
    
    def __init__(self):
        self.converter = None
        if OPENCC_AVAILABLE:
            try:
                # 嘗試不同的配置檔案名稱
                config_options = ['s2t', 's2t.json', 's2tw', 's2tw.json']

                for config in config_options:
                    try:
                        self.converter = opencc.OpenCC(config)
                        print(f"OpenCC初始化成功，使用配置: {config}")
                        break
                    except Exception as e:
                        continue

                if not self.converter:
                    print("OpenCC初始化失敗: 無法找到有效的配置檔案")

            except Exception as e:
                print(f"OpenCC初始化失敗: {e}")
                self.converter = None
    
    def is_simplified_chinese(self, text: str) -> bool:
        """
        檢測文字是否包含簡體中文
        
        Args:
            text: 要檢測的文字
            
        Returns:
            bool: 是否包含簡體中文
        """
        if not text:
            return False
        
        # 常見簡體字特徵
        simplified_chars = {
            '国', '发', '会', '说', '来', '对', '开', '关', '门', '问',
            '间', '时', '实', '现', '学', '业', '产', '经', '济', '社',
            '党', '政', '府', '军', '民', '众', '团', '体', '织', '组',
            '级', '别', '类', '种', '样', '式', '法', '规', '则', '制',
            '度', '系', '统', '结', '构', '建', '设', '计', '划', '案',
            '项', '目', '标', '准', '确', '定', '决', '议', '论', '证',
            '明', '显', '示', '表', '达', '述', '讲', '话', '言', '语',
            '词', '汇', '字', '符', '号', '码', '数', '量', '额', '价',
            '值', '费', '用', '成', '本', '利', '益', '效', '果', '应',
            '该', '须', '要', '需', '求', '供', '给', '提', '供', '献'
        }
        
        # 檢查是否包含簡體字
        for char in simplified_chars:
            if char in text:
                return True
        
        return False
    
    def convert_to_traditional(self, text: str) -> str:
        """
        將簡體中文轉換為正體中文
        
        Args:
            text: 要轉換的文字
            
        Returns:
            str: 轉換後的文字
        """
        if not text:
            return text
        
        if not self.converter:
            print("警告：OpenCC轉換器不可用，返回原文")
            return text
        
        try:
            # 使用OpenCC進行轉換
            converted_text = self.converter.convert(text)
            return converted_text
        except Exception as e:
            print(f"文字轉換失敗: {e}")
            return text
    
    def auto_convert_if_simplified(self, text: str) -> tuple[str, bool]:
        """
        自動檢測並轉換簡體中文
        
        Args:
            text: 要處理的文字
            
        Returns:
            tuple: (轉換後的文字, 是否進行了轉換)
        """
        if not text:
            return text, False
        
        # 檢測是否為簡體中文
        is_simplified = self.is_simplified_chinese(text)
        
        if is_simplified and self.converter:
            converted_text = self.convert_to_traditional(text)
            return converted_text, True
        
        return text, False
    
    def convert_html_content(self, html_content: str) -> tuple[str, bool]:
        """
        轉換HTML內容中的簡體中文
        
        Args:
            html_content: HTML內容
            
        Returns:
            tuple: (轉換後的HTML, 是否進行了轉換)
        """
        if not html_content:
            return html_content, False
        
        # 提取文字內容進行檢測
        text_pattern = r'>([^<]+)<'
        text_matches = re.findall(text_pattern, html_content)
        combined_text = ' '.join(text_matches)
        
        is_simplified = self.is_simplified_chinese(combined_text)
        
        if is_simplified and self.converter:
            try:
                converted_html = self.converter.convert(html_content)
                return converted_html, True
            except Exception as e:
                print(f"HTML轉換失敗: {e}")
                return html_content, False
        
        return html_content, False
    
    def get_conversion_stats(self, original_text: str, converted_text: str) -> dict:
        """
        獲取轉換統計資訊
        
        Args:
            original_text: 原始文字
            converted_text: 轉換後文字
            
        Returns:
            dict: 統計資訊
        """
        if not original_text or not converted_text:
            return {
                'total_chars': 0,
                'changed_chars': 0,
                'change_rate': 0.0
            }
        
        total_chars = len(original_text)
        changed_chars = sum(1 for a, b in zip(original_text, converted_text) if a != b)
        change_rate = (changed_chars / total_chars * 100) if total_chars > 0 else 0.0
        
        return {
            'total_chars': total_chars,
            'changed_chars': changed_chars,
            'change_rate': round(change_rate, 2)
        }
    
    def is_available(self) -> bool:
        """
        檢查轉換器是否可用
        
        Returns:
            bool: 轉換器是否可用
        """
        return self.converter is not None
    
    def get_status(self) -> str:
        """
        獲取轉換器狀態
        
        Returns:
            str: 狀態描述
        """
        if self.converter:
            return "OpenCC簡繁轉換器已就緒"
        elif OPENCC_AVAILABLE:
            return "OpenCC已安裝但初始化失敗"
        else:
            return "OpenCC未安裝，請執行: pip install opencc-python-reimplemented"


# 全域轉換器實例
text_converter = TextConverter()
