import logging
import os
from pathlib import Path
from datetime import datetime

# 获取当前工作目录
BASE_DIR = Path.cwd()

# 确保logs目录存在
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# 设置日志文件名（使用当前日期）
log_filename = LOGS_DIR / f"article_generator_{datetime.now().strftime('%Y%m%d')}.log"

# 配置日志记录器
logger = logging.getLogger('article_generator')
logger.setLevel(logging.INFO)

# 创建文件处理器
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.INFO)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 创建格式化器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 添加处理器到日志记录器
logger.addHandler(file_handler)
logger.addHandler(console_handler) 