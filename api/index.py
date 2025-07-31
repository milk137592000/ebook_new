import sys
import os

# 添加根目錄到Python路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel入口點
application = app

if __name__ == "__main__":
    app.run()
