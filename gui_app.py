import sys
import json
import os
import base64
from io import BytesIO
from pathlib import Path
import pickle
import asyncio
import aiohttp
import httpx
import random
import urllib.parse
import markdown
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                           QTextEdit, QScrollArea, QFrame, QFormLayout,
                           QMessageBox, QFileDialog, QCheckBox, QProgressDialog,
                           QGridLayout, QListWidget, QProgressBar, QSplitter,
                           QDialog, QGraphicsDropShadowEffect, QSizePolicy,
                           QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap
from PyQt6.QtCore import pyqtSignal
import re
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import QPropertyAnimation
from PyQt6.QtCore import QEasingCurve
from PyQt6.QtWidgets import QListWidgetItem
import psutil
import time
import jieba
import logging
# 禁用jieba的日志输出
jieba.setLogLevel(logging.INFO)
from PIL import Image
from backend.logger import logger  # 使用绝对导入

# 加载环境变量
load_dotenv()

# 获取当前工作目录
BASE_DIR = Path.cwd()

# 确保必要的目录存在
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# 图标文件的base64编码
ICON_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAd5JREFUWEftVu1xwjAMfSIDlGwAkxQmgRx0DmCOhiObNJ2kbBA6QFFPYBfH+bBi7sof/Ney/PT09EF48KEH/48ngLsYyHH6khSuMZ7GpjIawB7VkkEH+ZjB8zekZQyIBoADqskZmIWcMUavAC+vdlQQzp+hNyukhW/TAJDj9AEFgNBnHfdHP13/DaBcYzx3wUWnoI8BBm0ATAAcCbyztqoURFJbe5bjxFYba7xkfT6jq6DLqVsdBM7aou5NQZvjPaoNg5YMzkLlluP7YKsjAU8zpMe7GbhRioaKfedDbC8FrMm5G1Vf0xlKvxqANKcf0KXtirK7Wq9pzaJ+aOhXAxBDt0G1sWB0stWq3zKvSoEY+ywk4LkVmHcnw0ntV20oIOpR3lLhsqMpvcFlaB+YSGUCmmFFBcCSczu8Gq02JPJBDDipkIF1EZtzgiXaBmYwAHHyjmpGIAHxd2J3gsEAPB3UGJDBE2q9PgtqAM38X3uCceikg4oE512oBavK0GxHCwaJyGpbEoG3K6Q7x8b0AAuMStmSQoy0MnCNdrS5rVw14soEnPkRGoZaxQlQ2cVKKwC39ztflwQuJequ0rL7JIMWXYypNOAMFdloir5PlWAmXaNcLcJQQ4m9fwJ4OAO/Ad/XIUGq4v0AAAAASUVORK5CYII="

def get_app_icon():
    """获取应用图标"""
    global ICON_BASE64
    if ICON_BASE64 is None:
        try:
            # 如果base64为空，尝试从文件读取并转换
            icon_path = os.path.join(os.path.dirname(__file__), '1.png')
            if os.path.exists(icon_path):
                with open(icon_path, 'rb') as f:
                    ICON_BASE64 = base64.b64encode(f.read()).decode('utf-8')
                    # 将base64字符串写入到文件中
                    with open(__file__, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # 更新ICON_BASE64的值
                    new_content = content.replace('ICON_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAd5JREFUWEftVu1xwjAMfSIDlGwAkxQmgRx0DmCOhiObNJ2kbBA6QFFPYBfH+bBi7sof/Ney/PT09EF48KEH/48ngLsYyHH6khSuMZ7GpjIawB7VkkEH+ZjB8zekZQyIBoADqskZmIWcMUavAC+vdlQQzp+hNyukhW/TAJDj9AEFgNBnHfdHP13/DaBcYzx3wUWnoI8BBm0ATAAcCbyztqoURFJbe5bjxFYba7xkfT6jq6DLqVsdBM7aou5NQZvjPaoNg5YMzkLlluP7YKsjAU8zpMe7GbhRioaKfedDbC8FrMm5G1Vf0xlKvxqANKcf0KXtirK7Wq9pzaJ+aOhXAxBDt0G1sWB0stWq3zKvSoEY+ywk4LkVmHcnw0ntV20oIOpR3lLhsqMpvcFlaB+YSGUCmmFFBcCSczu8Gq02JPJBDDipkIF1EZtzgiXaBmYwAHHyjmpGIAHxd2J3gsEAPB3UGJDBE2q9PgtqAM38X3uCceikg4oE512oBavK0GxHCwaJyGpbEoG3K6Q7x8b0AAuMStmSQoy0MnCNdrS5rVw14soEnPkRGoZaxQlQ2cVKKwC39ztflwQuJequ0rL7JIMWXYypNOAMFdloir5PlWAmXaNcLcJQQ4m9fwJ4OAO/Ad/XIUGq4v0AAAAASUVORK5CYII="', f'ICON_BASE64 = "{ICON_BASE64}"')
                    with open(__file__, 'w', encoding='utf-8') as f:
                        f.write(new_content)
        except Exception as e:
            logger.error(f"读取图标文件失败: {str(e)}")
            return None
    
    if ICON_BASE64:
        try:
            # 从base64创建QIcon
            pixmap = QPixmap()
            pixmap.loadFromData(base64.b64decode(ICON_BASE64))
            return QIcon(pixmap)
        except Exception as e:
            logger.error(f"创建图标失败: {str(e)}")
    return None

class ThemeManager:
    """主题管理器"""
    DARK_THEME = {
        'background': '#1A1A1A',
        'primary': '#409EFF',
        'success': '#67C23A',
        'warning': '#E6A23C',
        'danger': '#F56C6C',
        'info': '#909399',
        'text': '#E4E7ED',
        'text_secondary': '#C0C4CC',
        'border': '#303030',
        'hover': '#2C2C2C',
        'card': '#2C2C2C',
        'shadow': 'rgba(0, 0, 0, 0.5)'
    }
    
    def __init__(self):
        self.current_theme = self.DARK_THEME
    
    def get_style(self, component: str) -> str:
        """获取组件样式"""
        if component == 'main_window':
            return f"""
                QMainWindow {{
                    background-color: {self.current_theme['background']};
                }}
                QScrollArea {{
                    border: none;
                    background-color: transparent;
                }}
                QScrollBar:vertical {{
                    border: none;
                    background-color: {self.current_theme['background']};
                    width: 6px;
                    margin: 0px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: {self.current_theme['border']};
                    border-radius: 3px;
                    min-height: 15px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background-color: {self.current_theme['text_secondary']};
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}
            """
        elif component == 'header':
            return f"""
                QLabel#headerLabel {{
                    color: {self.current_theme['primary']};
                    font-size: 20px;
                    font-weight: bold;
                    padding: 6px;
                }}
                QPushButton {{
                    background-color: {self.current_theme['primary']};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    background-color: {self.current_theme['primary']};
                    opacity: 0.9;
                }}
                QPushButton:pressed {{
                    background-color: {self.current_theme['primary']};
                    opacity: 0.8;
                }}
            """
        elif component == 'card':
            return f"""
                QFrame {{
                    background-color: {self.current_theme['card']};
                    border: 1px solid {self.current_theme['border']};
                    border-radius: 4px;
                    padding: 8px;
                    margin: 4px;
                }}
                QFrame:hover {{
                    border-color: {self.current_theme['primary']};
                    background-color: {self.current_theme['hover']};
                }}
                QLabel {{
                    color: {self.current_theme['text']};
                    font-size: 14px;
                }}
                QLabel#nameLabel {{
                    color: {self.current_theme['primary']};
                    font-size: 16px;
                    font-weight: bold;
                    padding-bottom: 4px;
                }}
                QLabel#descLabel {{
                    color: {self.current_theme['text_secondary']};
                    padding-bottom: 6px;
                }}
                QPushButton {{
                    background-color: {self.current_theme['primary']};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    background-color: {self.current_theme['primary']};
                    opacity: 0.9;
                }}
                QPushButton:pressed {{
                    background-color: {self.current_theme['primary']};
                    opacity: 0.8;
                }}
            """
        elif component == 'form':
            return f"""
                QLabel {{
                    color: {self.current_theme['text']};
                    font-size: 14px;
                    font-weight: bold;
                }}
                QLineEdit, QTextEdit {{
                    background-color: {self.current_theme['card']};
                    border: 1px solid {self.current_theme['border']};
                    border-radius: 4px;
                    padding: 6px;
                    color: {self.current_theme['text']};
                    font-size: 14px;
                }}
                QLineEdit:focus, QTextEdit:focus {{
                    border-color: {self.current_theme['primary']};
                }}
                QCheckBox {{
                    color: {self.current_theme['text']};
                    font-size: 14px;
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                }}
                QCheckBox::indicator:unchecked {{
                    border: 1px solid {self.current_theme['border']};
                    background-color: {self.current_theme['card']};
                    border-radius: 3px;
                }}
                QCheckBox::indicator:checked {{
                    border: 1px solid {self.current_theme['primary']};
                    background-color: {self.current_theme['primary']};
                    border-radius: 3px;
                }}
            """
        elif component == 'template':
            return f"""
                QListWidget {{
                    background-color: {self.current_theme['card']};
                    border: 1px solid {self.current_theme['border']};
                    border-radius: 4px;
                    padding: 4px;
                }}
                QListWidget::item {{
                    padding: 6px;
                    border-bottom: 1px solid {self.current_theme['border']};
                    color: {self.current_theme['text']};
                    font-size: 14px;
                }}
                QListWidget::item:selected {{
                    background-color: {self.current_theme['hover']};
                    color: {self.current_theme['primary']};
                }}
                QListWidget::item:hover {{
                    background-color: {self.current_theme['hover']};
                }}
            """
        elif component == 'preview':
            return f"""
                QTextEdit {{
                    background-color: {self.current_theme['card']};
                    border: 1px solid {self.current_theme['border']};
                    border-radius: 4px;
                    padding: 8px;
                    color: {self.current_theme['text']};
                    font-family: "Microsoft YaHei", Arial, sans-serif;
                    line-height: 1.5;
                    font-size: 14px;
                }}
                QTextEdit:focus {{
                    border-color: {self.current_theme['primary']};
                }}
                QPushButton {{
                    background-color: {self.current_theme['primary']};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    background-color: {self.current_theme['primary']};
                    opacity: 0.9;
                }}
                QPushButton:pressed {{
                    background-color: {self.current_theme['primary']};
                    opacity: 0.8;
                }}
            """
        return ""

class AnimatedButton(QPushButton):
    """带动画效果的按钮"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def enterEvent(self, event):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(-2, -2, 2, 2))
        self.animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(2, 2, -2, -2))
        self.animation.start()
        super().leaveEvent(event)

class Agent:
    def __init__(self, name: str, purpose: str, article_style: str, expertise: str, writing_style: str, prompt_template: str = None):
        self.name = name
        self.purpose = purpose
        self.article_style = article_style
        self.expertise = expertise
        self.writing_style = writing_style
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.prompt_template = prompt_template or """你是一位拥有十万粉丝的博主，请根据以下要求写一篇文章：

        文章标题：{title}
        补充要求：{requirements}

        写作要求：
        1. 核心要求：
           - 文章内容必须完全围绕标题 {title} 展开
           - 标题是文章的唯一主题，所有内容必须服务于标题
           - 补充要求 {requirements} 仅作为参考，不能影响文章的主题方向
           - 如果补充要求与标题主题不符，以标题为主

        2. 开头要求：
           - 必须直接回应标题 {title}
           - 介绍标题相关的背景和问题
           - 使用转折引出标题主题
           - 确保开头完全围绕标题展开

        3. 正文要求：
           - 包含5个小标题，每个小标题都要有数字标注
           - 每个小标题必须与标题 {title} 直接相关
           - 所有内容必须服务于标题主题
           - 在保持标题主题的前提下，可以适当参考补充要求
           - 引入与标题相关的具体事件、数据和报告
           - 使用韩寒式的语言风格：
             * 加入生动的比喻句
             * 使用疑问句引发思考
             * 适当使用祈使句增加互动感
           - 确保文章相似度低于20%，不能抄袭或翻译
           - 文章结构要清晰，段落之间要有逻辑连接
           - 每个段落长度适中，避免过长或过短
           - 使用适当的过渡词，使文章流畅自然

        4. 结尾要求：
           - 必须呼应标题 {title}
           - 总结标题相关的核心内容
           - 提出与标题相关的个人观点和总结
           - 给出与标题相关的启示和建议
           - 以标题相关的问题作为结尾，引发读者思考

        5. 语言风格：
           - 使用自然流畅的表达
           - 适当使用口语化表达
           - 加入个人观点和见解
           - 使用生动的比喻和例子
           - 在专业内容中适当加入幽默
           - 使用过渡词使文章连贯
           - 避免过于正式的表达

        6. 注意事项：
           - 不要使用"作为AI助手"等AI相关的表达
           - 避免使用过于完美的表达
           - 加入个人见解和思考
           - 使用更自然的表达方式
           - 文章内容必须完全围绕标题 {title} 展开
           - 确保文章内容完全符合标题的主题
           - 补充要求 {requirements} 仅作为参考，不能影响文章主题
           - 如果补充要求与标题主题不符，以标题为主

        请选择8个最重要的关键词（概念、术语或主题），用**标记出来。
        这些关键词应该：
        1. 必须与标题 {title} 直接相关
        2. 是文章的核心概念
        3. 具有代表性
        4. 适合配图
        5. 分布均匀，不要都集中在文章开头或结尾
        6. 每个关键词都应该出现在最合适的位置，与上下文紧密相关
        7. 关键词应该自然地融入文章，不影响阅读流畅性
        8. 关键词应该能够准确表达文章的核心内容

        配图要求：
        1. 只为最合适的关键词配图，确保图片与内容高度相关
        2. 图片应该能够增强文章的表现力
        3. 图片应该放在最合适的位置，不影响文章的整体布局
        4. 图片应该能够帮助读者更好地理解文章内容
        5. 避免过多配图，保持文章的简洁性

        请根据以上要求，以{name}的身份来写这篇文章。"""
    
    async def generate_article_with_deepseek(self, title: str, requirements: str, enable_web_search: bool = False) -> str:
        """使用DeepSeek生成文章"""
        try:
            # 检查API密钥
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if not api_key:
                raise Exception("DeepSeek API密钥未配置，请在.env文件中设置DEEPSEEK_API_KEY")
            
            # 1. 提取关键词
            logger.info("开始提取关键词...")
            keywords = await extract_keywords_with_deepseek(title, requirements)
            if not keywords:
                raise Exception("关键词提取失败")
            logger.info(f"提取的关键词: {keywords}")
            
            # 2. 构建提示词
            prompt = self.get_prompt(title, requirements)
            if not prompt:
                raise Exception("提示词生成失败")
            
            # 3. 添加关键词整合要求
            keyword_integration = """
请确保在文章中自然地融入以下关键词，不要生硬地插入：
{}
            
要求：
1. 关键词要自然地融入文章内容，符合上下文语境
2. 关键词可以适当变形或扩展，但核心含义要保持
3. 关键词的分布要均匀，不要集中在一处
4. 关键词的使用要符合文章的整体风格和语气
5. 关键词要服务于文章主题，不要为了使用而使用
""".format("\n".join([f"- {keyword}" for keyword in keywords]))
            
            prompt += keyword_integration
            
            # 4. 生成文章
            logger.info("开始生成文章...")
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        "https://api.deepseek.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "deepseek-chat",
                            "messages": [
                                {"role": "system", "content": "你是一个专业的文章写作助手，擅长创作高质量的文章。"},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.7,
                            "max_tokens": 4000
                        },
                        timeout=60.0
                    )
                    
                    if response.status_code != 200:
                        error_msg = f"DeepSeek API请求失败，状态码: {response.status_code}"
                        if response.text:
                            error_msg += f"\n响应内容: {response.text}"
                        raise Exception(error_msg)
                    
                    result = response.json()
                    if 'choices' not in result or not result['choices']:
                        raise Exception("DeepSeek API响应格式错误")
                    
                    article = result['choices'][0]['message']['content']
                    if not article:
                        raise Exception("文章内容为空")
                    
                    # 5. 检查关键词使用情况
                    keyword_usage = {keyword: article.count(keyword) for keyword in keywords}
                    unused_keywords = [k for k, v in keyword_usage.items() if v == 0]
                    
                    if unused_keywords:
                        logger.info(f"以下关键词未在文章中使用: {unused_keywords}")
                        # 如果有未使用的关键词，重新生成文章
                        prompt += f"\n\n请确保在文章中包含以下未使用的关键词: {', '.join(unused_keywords)}"
                        
                        response = await client.post(
                            "https://api.deepseek.com/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {api_key}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "model": "deepseek-chat",
                                "messages": [
                                    {"role": "system", "content": "你是一个专业的文章写作助手，擅长创作高质量的文章。"},
                                    {"role": "user", "content": prompt}
                                ],
                                "temperature": 0.7,
                                "max_tokens": 4000
                            },
                            timeout=60.0
                        )
                        
                        if response.status_code != 200:
                            error_msg = f"DeepSeek API重试请求失败，状态码: {response.status_code}"
                            if response.text:
                                error_msg += f"\n响应内容: {response.text}"
                            raise Exception(error_msg)
                        
                        result = response.json()
                        if 'choices' not in result or not result['choices']:
                            raise Exception("DeepSeek API重试响应格式错误")
                        
                        article = result['choices'][0]['message']['content']
                        if not article:
                            raise Exception("重试生成的文章内容为空")
                    
                    logger.info("文章生成成功")
                    return article
                    
                except httpx.TimeoutException:
                    raise Exception("DeepSeek API请求超时，请检查网络连接")
                except httpx.RequestError as e:
                    raise Exception(f"DeepSeek API请求失败: {str(e)}")
                except json.JSONDecodeError as e:
                    raise Exception(f"DeepSeek API响应解析失败: {str(e)}")
                    
        except Exception as e:
            logger.error(f"文章生成失败: {str(e)}")
            raise Exception(f"文章生成失败: {str(e)}")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'name': self.name,
            'purpose': self.purpose,
            'article_style': self.article_style,
            'expertise': self.expertise,
            'writing_style': self.writing_style,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'prompt_template': self.prompt_template
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Agent':
        """从字典创建实例"""
        agent = cls(
            name=data['name'],
            purpose=data['purpose'],
            article_style=data['article_style'],
            expertise=data['expertise'],
            writing_style=data['writing_style'],
            prompt_template=data.get('prompt_template')
        )
        agent.created_at = datetime.fromisoformat(data['created_at'])
        agent.updated_at = datetime.fromisoformat(data['updated_at'])
        return agent
    
    def save(self):
        """保存智能体到文件"""
        file_path = MODELS_DIR / f"{self.name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, name: str) -> Optional['Agent']:
        """从文件加载智能体"""
        file_path = MODELS_DIR / f"{name}.json"
        if not file_path.exists():
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return cls.from_dict(data)
    
    @classmethod
    def list_all(cls) -> List['Agent']:
        """列出所有智能体"""
        agents = []
        
        # 确保models目录存在
        MODELS_DIR.mkdir(exist_ok=True)
        
        # 如果没有智能体文件，创建一个默认智能体
        if not any(MODELS_DIR.glob("*.json")):
            default_agent = cls(
                name="默认智能体",
                purpose="生成高质量的文章",
                article_style="专业、客观、深入",
                expertise="写作、编辑、内容创作",
                writing_style="清晰、流畅、有说服力"
            )
            default_agent.save()
            agents.append(default_agent)
            return agents
        
        # 加载所有智能体文件
        for file_path in MODELS_DIR.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    agent = cls.from_dict(data)
                    agents.append(agent)
            except Exception:
                continue
                
        return sorted(agents, key=lambda x: x.created_at, reverse=True)
    
    def delete(self):
        """删除智能体文件"""
        file_path = MODELS_DIR / f"{self.name}.json"
        if file_path.exists():
            file_path.unlink()

    def get_prompt(self, title: str, requirements: str) -> str:
        """生成完整的提示词"""
        return self.prompt_template.format(
            title=title,
            requirements=requirements,
            name=self.name,
            writing_style=self.writing_style,
            article_style=self.article_style,
            expertise=self.expertise,
            purpose=self.purpose
        )

class WebSearcher:
    """网络搜索器"""
    def __init__(self):
        self.session = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def search_baike(self, query: str) -> Optional[Dict]:
        """搜索百度百科"""
        try:
            url = f"https://baike.baidu.com/item/{urllib.parse.quote(query)}"
            async with self.session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    return None
                    
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # 提取百科内容
                content = soup.select_one('.lemma-summary')
                if not content:
                    return None
                    
                # 提取更新时间
                update_time = soup.select_one('.j-update-time')
                time_str = update_time.text.strip() if update_time else "未知"
                
                return {
                    'title': query,
                    'url': url,
                    'content': content.text.strip(),
                    'source': '百度百科',
                    'time': time_str
                }
        except Exception:
            return None
            
    async def search_official_media(self, query: str) -> List[Dict]:
        """搜索官方媒体"""
        official_sites = [
            ("人民网", "http://search.people.com.cn/cnpeople/news/getNewsResult.jsp"),
            ("新华网", "http://so.news.cn/getNews"),
            ("央视网", "http://search.cctv.com/search.php"),
            ("光明网", "http://search.gmw.cn/"),
            ("中国网", "http://search.china.com.cn/"),
            ("中国政府网", "http://sousuo.gov.cn/"),
            ("国务院新闻办公室", "http://www.scio.gov.cn/"),
            ("中央广播电视总台", "http://search.cnr.cn/"),
            ("中国日报网", "http://search.chinadaily.com.cn/")
        ]
        
        results = []
        for site_name, base_url in official_sites:
            try:
                if "people.com.cn" in base_url:
                    params = {
                        "keyword": query,
                        "pageSize": 10,
                        "pageNum": 1
                    }
                    async with self.session.get(base_url, params=params, timeout=10) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            for item in data.get('list', []):
                                results.append({
                                    'title': item.get('title', ''),
                                    'url': item.get('url', ''),
                                    'source': site_name,
                                    'time': item.get('date', ''),
                                    'type': 'official'
                                })
                elif "news.cn" in base_url:  # 新华网
                    params = {
                        "keyword": query,
                        "pageSize": 10,
                        "pageNum": 1
                    }
                    async with self.session.get(base_url, params=params, timeout=10) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            for item in data.get('data', []):
                                results.append({
                                    'title': item.get('title', ''),
                                    'url': item.get('url', ''),
                                    'source': site_name,
                                    'time': item.get('publishTime', ''),
                                    'type': 'official'
                                })
                # 其他网站的搜索实现类似...
            except Exception:
                continue
                
        return results
        
    async def search_weibo(self, query: str) -> List[Dict]:
        """搜索微博内容"""
        url = "https://s.weibo.com/weibo"
        params = {
            "q": query,
            "typeall": 1,
            "suball": 1,
            "timescope": "custom:2023-01-01-0:2024-12-31-23",
            "Refer": "g"
        }
        
        try:
            async with self.session.get(url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return []
                    
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                results = []
                
                for item in soup.select('.card-wrap'):
                    title = item.select_one('.txt')
                    author = item.select_one('.name')
                    time = item.select_one('.from')
                    
                    if title and author and time:
                        results.append({
                            'title': title.get_text(strip=True),
                            'author': author.get_text(strip=True),
                            'time': time.get_text(strip=True),
                            'url': f"https://s.weibo.com{title.find('a')['href']}" if title.find('a') else None
                        })
                        
            return results
        except Exception:
            return []

    async def search_douyin(self, query: str) -> List[Dict]:
        """搜索抖音内容"""
        url = "https://www.douyin.com/search"
        params = {
            "keyword": query,
            "type": "video"
        }
        
        try:
            async with self.session.get(url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return []
                
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                results = []
                
                for item in soup.select('.video-card'):
                    title = item.select_one('.title')
                    author = item.select_one('.author')
                    time = item.select_one('.time')
                    
                    if title and author and time:
                        results.append({
                            'title': title.get_text(strip=True),
                            'author': author.get_text(strip=True),
                            'time': time.get_text(strip=True),
                            'url': f"https://www.douyin.com{title.find('a')['href']}" if title.find('a') else None
                        })
                        
            return results
        except Exception:
            return []

    async def search(self, query: str, max_results: int = 20) -> List[Dict]:
        """综合搜索"""
        tasks = [
            self.search_baike(query),
            self.search_official_media(query),
            self.search_weibo(query),
            self.search_douyin(query)
        ]
        
        results = []
        search_results = await asyncio.gather(*tasks)
        
        # 合并所有搜索结果
        for result in search_results:
            if isinstance(result, list):
                results.extend(result)
            elif result:  # 单个结果（如百科）
                results.append(result)
                
        # 按时间排序
        results.sort(key=lambda x: x.get('time', ''), reverse=True)
        
        # 去重
        seen = set()
        unique_results = []
        for item in results:
            key = (item.get('title', ''), item.get('url', ''))
            if key not in seen:
                seen.add(key)
                unique_results.append(item)
                
        return unique_results[:max_results]

class ArticleGenerator(QThread):
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str, int)
    error = pyqtSignal(str)
    
    def __init__(self, title: str, requirements: str, agent: Agent, enable_web_search: bool):
        super().__init__()
        self.title = title
        self.requirements = requirements
        self.agent = agent
        self.enable_web_search = enable_web_search
        self.is_cancelled = False
        
    def run(self):
        try:
            asyncio.run(self.generate())
        except Exception as e:
            self.error.emit(str(e))
            
    async def generate(self):
        try:
            # 1. 文章生成阶段
            self.progress.emit("正在分析文章主题和结构...", 20)
            try:
                article = await self.agent.generate_article_with_deepseek(
                    self.title, 
                    self.requirements,
                    self.enable_web_search
                )
                if not article:
                    raise Exception("文章生成失败，请检查DeepSeek API配置")
            except Exception as e:
                logger.error(f"文章生成失败: {str(e)}")
                raise Exception(f"文章生成失败: {str(e)}")
            
            self.progress.emit("正在优化文章内容和表达...", 30)
            
            # 2. 关键词提取阶段
            self.progress.emit("正在提取文章关键词...", 40)
            
            # 获取联网搜索结果
            web_search_results = ""
            if self.enable_web_search:
                try:
                    async with WebSearcher() as searcher:
                        search_results = await searcher.search(self.title)
                        if search_results:
                            # 按来源分类整理搜索结果
                            official_results = [r for r in search_results if r.get('type') == 'official']
                            social_results = [r for r in search_results if r.get('type') == 'social']
                            baike_result = next((r for r in search_results if r.get('source') == '百度百科'), None)
                            
                            # 构建搜索结果摘要
                            web_search_results = f"关于'{self.title}'的网络搜索结果：\n\n"
                            
                            if baike_result:
                                web_search_results += f"【背景知识】\n{baike_result['content']}\n\n"
                            
                            if official_results:
                                web_search_results += "【官方媒体报道】\n"
                                for item in official_results[:5]:  # 取前5条
                                    web_search_results += f"- {item['title']}（{item['source']}，{item['time']}）\n"
                                    web_search_results += f"  内容：{item['content']}\n\n"
                            
                            if social_results:
                                web_search_results += "【社交媒体热点】\n"
                                for item in social_results[:5]:  # 取前5条
                                    web_search_results += f"- {item['title']}（{item['source']}，{item['time']}）\n"
                                    web_search_results += f"  内容：{item['content']}\n\n"
                except Exception as e:
                    logger.error(f"网络搜索失败: {str(e)}")
                    # 继续执行，不中断流程
            
            # 首先尝试使用Deepseek生成关键词
            try:
                keywords = await extract_keywords_with_deepseek(self.title, web_search_results)
            except Exception as e:
                logger.error(f"Deepseek关键词提取失败: {str(e)}")
                keywords = []
            
            # 如果Deepseek生成失败，使用备用方法从文章中提取
            if not keywords:
                self.progress.emit("使用备用方法提取关键词...", 42)
                try:
                    keywords = extract_keywords(article, max_keywords=8)
                except Exception as e:
                    logger.error(f"备用关键词提取失败: {str(e)}")
                    keywords = []
            
            if not keywords:
                raise Exception("无法提取关键词，请检查文章内容")
            
            self.progress.emit(f"已提取 {len(keywords)} 个关键词，准备搜索图片...", 45)
            
            # 3. 图片搜索阶段
            keyword_images = {}
            try:
                async with ImageSearcher() as image_searcher:
                    for i, keyword in enumerate(keywords):
                        if self.is_cancelled:
                            return
                        self.progress.emit(f"正在搜索第 {i+1} 个关键词的图片...", 50 + (i * 5))
                        try:
                            # 获取关键词上下文
                            context = extract_keyword_context(article, keyword)
                            # 搜索图片
                            image_urls = await search_one(keyword, None, context, image_searcher, self.enable_web_search)
                            if image_urls:
                                # 确保image_urls是列表
                                if not isinstance(image_urls, list):
                                    image_urls = [image_urls]
                                
                                # 清理URL
                                cleaned_urls = []
                                for url in image_urls:
                                    if url.startswith(('http://', 'https://')):
                                        # 清理URL中的转义字符
                                        url = url.replace('\\/', '/')
                                        url = url.replace('\\u002F', '/')
                                        url = url.replace('\\u003D', '=')
                                        url = url.replace('\\u0026', '&')
                                        url = url.replace('\\u0023', '#')
                                        url = url.replace('\\u003F', '?')
                                        url = url.replace('\\u002B', '+')
                                        url = url.replace('\\u0020', ' ')
                                        url = url.replace('\\u0025', '%')
                                        url = url.replace('\\u0022', '"')
                                        url = url.replace('\\u0027', "'")
                                        url = url.replace('\\u005C', '\\')
                                        url = url.replace('\\u003A', ':')
                                        url = url.replace('\\u002C', ',')
                                        url = url.replace('\\u002E', '.')
                                        url = url.replace('\\u002D', '-')
                                        url = url.replace('\\u005F', '_')
                                        url = url.replace('\\u007E', '~')
                                        url = url.replace('\\u0021', '!')
                                        url = url.replace('\\u0028', '(')
                                        url = url.replace('\\u0029', ')')
                                        url = url.replace('\\u002A', '*')
                                        url = url.replace('\\u003B', ';')
                                        url = url.replace('\\u003C', '<')
                                        url = url.replace('\\u003E', '>')
                                        url = url.replace('\\u0040', '@')
                                        url = url.replace('\\u005B', '[')
                                        url = url.replace('\\u005D', ']')
                                        url = url.replace('\\u005E', '^')
                                        url = url.replace('\\u0060', '`')
                                        url = url.replace('\\u007B', '{')
                                        url = url.replace('\\u007D', '}')
                                        url = url.replace('\\u007C', '|')
                                        
                                        # 确保URL是有效的
                                        try:
                                            parsed = urllib.parse.urlparse(url)
                                            if parsed.scheme and parsed.netloc:
                                                cleaned_urls.append(url)
                                        except:
                                            continue
                                        
                                if cleaned_urls:
                                    keyword_images[keyword] = cleaned_urls
                                    logger.info(f"为关键词 '{keyword}' 找到 {len(cleaned_urls)} 张图片")
                        except Exception as e:
                            logger.error(f"搜索关键词 '{keyword}' 的图片失败: {str(e)}")
                            continue
            except Exception as e:
                logger.error(f"图片搜索失败: {str(e)}")
                # 继续执行，不中断流程
            
            self.progress.emit(f"已找到 {len(keyword_images)} 个关键词的图片，准备插入...", 70)
            
            # 4. 图片插入和排版阶段
            self.progress.emit("正在插入图片并排版...", 80)
            try:
                formatted_article = await insert_images_to_article(article, keyword_images)
                logger.info("图片插入完成，文章内容预览:")
                logger.info(formatted_article[:500] + "...")  # 打印前500个字符用于调试
            except Exception as e:
                logger.error(f"图片插入失败: {str(e)}")
                formatted_article = article  # 使用原始文章
            
            self.progress.emit("文章生成完成！", 100)
            
            # 生成文件ID（使用标题和时间戳）
            current_time = datetime.now()
            timestamp = current_time.strftime("%Y%m%d-%H%M%S")
            # 清理标题中的非法字符
            clean_title = re.sub(r'[\\/:*?"<>|]', '_', self.title)
            file_id = f"{clean_title}-{timestamp}"
            
            # 返回结果
            result = {
                'file_id': file_id,
                'article': formatted_article,
                'keywords': keywords,
                'images': keyword_images
            }
            
            self.finished.emit(result)
            
        except Exception as e:
            logger.error(f"文章生成过程出错: {str(e)}")
            self.error.emit(str(e))

async def extract_keywords_with_deepseek(title: str, web_search_results: str = "") -> List[str]:
    """使用Deepseek根据标题和联网搜索信息生成关键词"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")
        
    api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 构建提示词
    prompt = f"""请根据以下标题和相关信息，生成8个最相关的关键词。
标题：{title}

要求：
1. 关键词必须与标题主题高度相关
2. 关键词应该涵盖文章的主要方面
3. 关键词应该具体且有意义
4. 关键词之间应该有一定的区分度
5. 关键词应该适合用于图片搜索

请直接返回关键词列表，每个关键词用逗号分隔，不要包含其他内容。"""

    if web_search_results:
        prompt += f"\n\n相关背景信息：\n{web_search_results}\n\n请确保生成的关键词与以上信息相关。"
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个专业的关键词提取助手，擅长从文本中提取最相关的关键词。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 200
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, headers=headers, json=data) as resp:
                if resp.status != 200:
                    raise Exception(f"API请求失败: {resp.status}")
                    
                result = await resp.json()
                if "choices" in result and len(result["choices"]) > 0:
                    keywords_text = result["choices"][0]["message"]["content"]
                    # 清理和分割关键词
                    keywords = [k.strip() for k in keywords_text.split(',')]
                    keywords = [k for k in keywords if k]  # 移除空关键词
                    return keywords[:8]  # 确保最多返回8个关键词
    except Exception as e:
        logger.error(f"使用Deepseek生成关键词失败: {str(e)}")
        return None

def extract_keywords(article, max_keywords=8):
    """从文章中提取关键词，考虑主题相关性和位置权重"""
    # 移除Markdown标记
    article = re.sub(r'#+\s+', '', article)  # 移除标题
    article = re.sub(r'!\[.*?\]\(.*?\)', '', article)  # 移除图片
    article = re.sub(r'\[.*?\]\(.*?\)', '', article)  # 移除链接
    article = re.sub(r'`.*?`', '', article)  # 移除代码
    article = re.sub(r'\*\*.*?\*\*', '', article)  # 移除加粗
    article = re.sub(r'\*.*?\*', '', article)  # 移除斜体
    
    # 获取文章标题（第一行）
    title = article.split('\n')[0].strip()
    
    # 分词
    words = jieba.cut(article)
    word_freq = {}
    word_positions = {}
    word_scores = {}
    
    # 统计词频和位置
    for i, word in enumerate(words):
        if len(word) > 1:  # 忽略单字
            word_freq[word] = word_freq.get(word, 0) + 1
            if word not in word_positions:
                word_positions[word] = []
            word_positions[word].append(i)
    
    # 计算每个词的重要性得分
    for word in word_freq:
        # 基础分：词频
        score = word_freq[word]
        
        # 位置权重：出现在文章开头和结尾的词更重要
        positions = word_positions[word]
        if positions:
            first_pos = positions[0]
            last_pos = positions[-1]
            total_words = max(word_positions.values(), key=lambda x: max(x))[0] if word_positions else 1
            
            # 开头和结尾的权重更高
            if first_pos < total_words * 0.2:  # 前20%
                score *= 1.5
            if last_pos > total_words * 0.8:  # 后20%
                score *= 1.3
            
            # 标题中的词权重更高
            if word in title:
                score *= 2.0
        
        word_scores[word] = score
    
    # 按得分排序
    sorted_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
    
    # 返回前N个关键词
    return [word for word, _ in sorted_words[:max_keywords]]

async def insert_images_to_article(article: str, keyword_images: Dict[str, List[str]]) -> str:
    """将图片插入到文章中"""
    try:
        # 1. 按关键词长度排序，优先处理长关键词
        sorted_keywords = sorted(keyword_images.keys(), key=len, reverse=True)
        
        # 2. 分割文章为段落
        paragraphs = article.split('\n')
        result = []
        
        # 3. 记录已使用的关键词
        used_keywords = set()
        
        # 4. 遍历每个段落
        for para in paragraphs:
            # 跳过标题和空段落
            if para.startswith('#') or not para.strip():
                result.append(para)
                continue
                
            # 添加当前段落
            result.append(para)
            
            # 检查是否需要插入图片
            for keyword in sorted_keywords:
                # 如果关键词已使用过，跳过
                if keyword in used_keywords:
                    continue
                    
                # 检查关键词是否在当前段落中
                if keyword in para:
                    # 获取该关键词的图片
                    images = keyword_images.get(keyword, [])
                    if images:
                        # 只取第一张图片
                        image_url = images[0]
                        # 处理抖音图片链接
                        if 'douyinpic.com' in image_url:
                            try:
                                # 解析URL
                                parsed_url = urllib.parse.urlparse(image_url)
                                query_params = urllib.parse.parse_qs(parsed_url.query)
                                
                                # 获取图片ID
                                path_parts = parsed_url.path.split('/')
                                img_id = path_parts[-1] if path_parts else None
                                
                                if img_id:
                                    # 使用多个CDN节点
                                    cdn_nodes = [
                                        'p3-pc-sign.douyinpic.com',
                                        'p1-pc-sign.douyinpic.com',
                                        'p9-pc-sign.douyinpic.com'
                                    ]
                                    
                                    # 尝试不同的CDN节点
                                    for cdn in cdn_nodes:
                                        # 构造新的URL，保留原始签名和过期时间
                                        new_url = f"https://{cdn}/obj/{img_id}"
                                        if query_params:
                                            new_url += '?' + urllib.parse.urlencode(query_params, doseq=True)
                                        
                                        # 检查URL是否可访问
                                        try:
                                            async with aiohttp.ClientSession() as session:
                                                async with session.head(new_url, timeout=5) as response:
                                                    if response.status == 200:
                                                        image_url = new_url
                                                        break
                                        except:
                                            continue
                            except Exception as e:
                                logger.error(f"处理抖音图片链接失败: {str(e)}")
                                # 如果处理失败，保持原始URL
                        
                        # 使用Markdown格式插入图片
                        result.append(f"\n![{keyword}相关图片]({image_url})\n")
                        # 标记关键词已使用
                        used_keywords.add(keyword)
                        logger.info(f"在段落中插入图片: {keyword}")
                        break
        
        # 5. 在文章末尾添加未使用的关键词图片
        if len(used_keywords) < len(sorted_keywords):
            result.append("\n---\n")
            result.append("### 相关图片\n")
            
            # 为每个未使用的关键词添加一张图片
            for keyword in sorted_keywords:
                if keyword not in used_keywords:
                    images = keyword_images.get(keyword, [])
                    if images:
                        image_url = images[0]
                        # 处理抖音图片链接
                        if 'douyinpic.com' in image_url:
                            try:
                                # 解析URL
                                parsed_url = urllib.parse.urlparse(image_url)
                                query_params = urllib.parse.parse_qs(parsed_url.query)
                                
                                # 获取图片ID
                                path_parts = parsed_url.path.split('/')
                                img_id = path_parts[-1] if path_parts else None
                                
                                if img_id:
                                    # 使用多个CDN节点
                                    cdn_nodes = [
                                        'p3-pc-sign.douyinpic.com',
                                        'p1-pc-sign.douyinpic.com',
                                        'p9-pc-sign.douyinpic.com'
                                    ]
                                    
                                    # 尝试不同的CDN节点
                                    for cdn in cdn_nodes:
                                        # 构造新的URL，保留原始签名和过期时间
                                        new_url = f"https://{cdn}/obj/{img_id}"
                                        if query_params:
                                            new_url += '?' + urllib.parse.urlencode(query_params, doseq=True)
                                        
                                        # 检查URL是否可访问
                                        try:
                                            async with aiohttp.ClientSession() as session:
                                                async with session.head(new_url, timeout=5) as response:
                                                    if response.status == 200:
                                                        image_url = new_url
                                                        break
                                        except:
                                            continue
                            except Exception as e:
                                logger.error(f"处理抖音图片链接失败: {str(e)}")
                                # 如果处理失败，保持原始URL
                        
                        result.append(f"\n#### {keyword}相关图片\n")
                        result.append(f"![{keyword}相关图片]({image_url})")
                        logger.info(f"在文章末尾添加图片: {keyword}")
        
        # 6. 合并结果
        final_article = '\n'.join(result)
        logger.info("图片插入完成")
        return final_article
        
    except Exception as e:
        logger.error(f"插入图片失败: {str(e)}")
        return article

async def generate_image_query(llm_api_key, keyword, article):
    """生成图片搜索查询"""
    # 直接返回关键词，不生成图片描述
    return keyword

def extract_keyword_context(article: str, keyword: str, max_chars: int = 500) -> str:
    """提取关键词的上下文，增强上下文提取逻辑"""
    try:
        # 1. 分割文章为段落
        paragraphs = article.split('\n')
        
        # 2. 找到包含关键词的段落
        relevant_paragraphs = []
        for para in paragraphs:
            if keyword in para:
                # 清理段落中的Markdown标记
                para = re.sub(r'[*#_~`]', '', para)
                para = re.sub(r'\[.*?\]\(.*?\)', '', para)
                para = re.sub(r'<.*?>', '', para)
                para = para.strip()
                if para:
                    relevant_paragraphs.append(para)
        
        # 3. 如果找到相关段落，返回它们
        if relevant_paragraphs:
            context = ' '.join(relevant_paragraphs)
            return context[:max_chars]
        
        # 4. 如果没有找到相关段落，返回文章开头部分
        return article[:max_chars]
        
    except Exception as e:
        logger.error(f"提取关键词上下文失败: {str(e)}")
        return ""

async def check_image_quality(url):
    """检查图片质量"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    # 获取图片大小
                    content_length = response.headers.get('Content-Length')
                    if content_length:
                        size = int(content_length)
                        # 检查图片大小是否合适（至少50KB，最大10MB）
                        if size < 50 * 1024 or size > 10 * 1024 * 1024:
                            return False
                    
                    # 获取图片类型
                    content_type = response.headers.get('Content-Type', '')
                    if not content_type.startswith('image/'):
                        return False
                    
                    # 获取图片尺寸
                    try:
                        img_data = await response.read()
                        img = Image.open(BytesIO(img_data))
                        width, height = img.size
                        # 检查图片尺寸是否合适（至少300x300）
                        if width < 300 or height < 300:
                            return False
                    except:
                        return False
                    
                    return True
    except Exception:
        return False

async def check_image_relevance(url, keyword, context):
    """检查图片与关键词的相关性，增强相关性检查"""
    try:
        # 1. 检查URL是否包含关键词
        url_lower = url.lower()
        keyword_lower = keyword.lower()
        
        # 2. 构建关键词变体列表
        keyword_variants = [
            keyword_lower,
            keyword_lower.replace(' ', ''),
            keyword_lower.replace(' ', '-'),
            keyword_lower.replace(' ', '_'),
            keyword_lower.replace(' ', '+'),
            keyword_lower.replace(' ', '.')
        ]
        
        # 3. 检查URL是否包含关键词或其变体
        if any(variant in url_lower for variant in keyword_variants):
            return True
            
        # 4. 检查URL是否包含相关词
        related_words = {
            '图片': ['image', 'photo', 'pic', 'img', 'picture', 'photograph'],
            '照片': ['photo', 'picture', 'photograph', 'image', 'pic'],
            '图': ['image', 'picture', 'graph', 'photo', 'pic'],
            '照': ['photo', 'picture', 'image'],
            '摄影': ['photography', 'photo', 'shoot'],
            '拍摄': ['shoot', 'photograph', 'photo'],
            '作品': ['work', 'artwork', 'creation']
        }
        
        for word, variants in related_words.items():
            if word in keyword_lower:
                if any(variant in url_lower for variant in variants):
                    return True
                    
        # 5. 检查URL是否包含上下文中的关键词
        if context:
            # 使用jieba分词提取上下文中的关键词
            words = jieba.cut(context)
            for word in words:
                if len(word) > 1 and word.lower() in url_lower:
                    return True
                    
        # 6. 检查URL是否包含常见的图片格式
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        if any(ext in url_lower for ext in image_extensions):
            return True
            
        return False
    except Exception as e:
        logger.error(f"检查图片相关性失败: {str(e)}")
        return False

async def check_image_similarity(url1: str, url2: str) -> bool:
    """检查两张图片是否相似"""
    try:
        # 如果URL完全相同，直接返回True
        if url1 == url2:
            return True
            
        # 如果URL相似（可能是同一张图片的不同尺寸版本）
        url1_parts = urllib.parse.urlparse(url1)
        url2_parts = urllib.parse.urlparse(url2)
        
        # 检查域名是否相同
        if url1_parts.netloc != url2_parts.netloc:
            return False
            
        # 检查路径是否相似
        path1 = url1_parts.path.lower()
        path2 = url2_parts.path.lower()
        
        # 如果路径完全相同，返回True
        if path1 == path2:
            return True
            
        # 检查是否是同一张图片的不同尺寸版本
        size_patterns = [
            r'(\d+)x(\d+)',
            r'(\d+)X(\d+)',
            r'(\d+)[xX](\d+)',
            r'(\d+)[_\-](\d+)',
            r'(\d+)p',
            r'(\d+)P',
            r'(\d+)px',
            r'(\d+)PX'
        ]
        
        # 移除尺寸信息后比较
        for pattern in size_patterns:
            path1 = re.sub(pattern, '', path1)
            path2 = re.sub(pattern, '', path2)
            
        if path1 == path2:
            return True
            
        return False
    except Exception as e:
        logger.error(f"检查图片相似度失败: {str(e)}")
        return False

async def deduplicate_images(image_urls: List[str]) -> List[str]:
    """去除重复和相似的图片"""
    try:
        unique_images = []
        for url in image_urls:
            # 检查是否与已选图片相似
            is_similar = False
            for unique_url in unique_images:
                if await check_image_similarity(url, unique_url):
                    is_similar = True
                    break
                    
            if not is_similar:
                unique_images.append(url)
                
        return unique_images
    except Exception as e:
        logger.error(f"图片去重失败: {str(e)}")
        return image_urls

async def search_one(keyword, llm_api_key, article, image_searcher, enable_web_search):
    """搜索单个关键词的图片，优化搜索策略"""
    try:
        # 1. 获取关键词上下文
        context = extract_keyword_context(article, keyword)
        
        # 2. 获取文章标题
        title = article.split('\n')[0].strip('#').strip()
        
        # 3. 构建搜索查询
        search_queries = [
            f"{title} {keyword}",  # 标题 + 关键词
            f"{keyword} {title}",  # 关键词 + 标题
            keyword,               # 仅关键词
            f"{keyword} 高清",     # 关键词 + 高清
            f"{keyword} 图片",     # 关键词 + 图片
            f"{keyword} 照片"      # 关键词 + 照片
        ]
        
        all_images = []
        # 4. 按顺序尝试不同的搜索源
        for query in search_queries:
            # 4.1 尝试百度百科
            baike_images = await image_searcher.crawl_baike_images(query, context)
            if baike_images:
                all_images.extend(baike_images)
                
            # 4.2 尝试百度图片
            baidu_images = await image_searcher.crawl_baidu_images(query, context)
            if baidu_images:
                all_images.extend(baidu_images)
                
            # 4.3 如果启用网络搜索，尝试Unsplash
            if enable_web_search:
                unsplash_images = await image_searcher.crawl_unsplash_images(query, context)
                if unsplash_images:
                    all_images.extend(unsplash_images)
                    
        # 5. 去重并限制数量
        unique_images = await deduplicate_images(all_images)
        return unique_images[:10]  # 返回最多10张不重复的图片
        
    except Exception as e:
        logger.error(f"搜索图片时出错: {str(e)}")
        return []

async def search_images_for_keywords(keywords, llm_api_key, article, image_searcher, enable_web_search):
    """为多个关键词搜索图片"""
    keyword_images = {}
    
    # 获取文章标题
    title = article.split('\n')[0].strip('#').strip()
    
    for keyword in keywords:
        try:
            # 组合标题和关键词
            combined_query = f"{title} {keyword}"
            
            # 获取关键词上下文
            context = extract_keyword_context(article, keyword)
            
            # 生成图片搜索查询
            image_query = await generate_image_query(llm_api_key, keyword, article)
            
            # 1. 优先从百度图片获取
            logger.info(f"正在从百度图片爬取关键词 '{keyword}' 的图片...")
            baidu_images = await image_searcher.crawl_baidu_images(combined_query, context)
            if baidu_images:
                keyword_images[keyword] = baidu_images
                logger.info(f"成功从百度图片获取到 {len(baidu_images)} 张图片")
                continue
                
            # 2. 如果百度图片没有，尝试百度百科
            logger.info(f"百度图片未找到合适图片，正在从百度百科爬取关键词 '{keyword}' 的图片...")
            baike_images = await image_searcher.crawl_baike_images(combined_query, context)
            if baike_images:
                keyword_images[keyword] = baike_images
                logger.info(f"成功从百度百科获取到 {len(baike_images)} 张图片")
                continue
                
            # 3. 如果百度百科也没有，尝试Unsplash
            if enable_web_search:
                logger.info(f"百度百科未找到合适图片，正在从Unsplash爬取关键词 '{keyword}' 的图片...")
                unsplash_images = await image_searcher.crawl_unsplash_images(combined_query, context)
                if unsplash_images:
                    keyword_images[keyword] = unsplash_images
                    logger.info(f"成功从Unsplash获取到 {len(unsplash_images)} 张图片")
                    continue
                    
            logger.warning(f"未能找到关键词 '{keyword}' 的合适图片")
            
        except Exception as e:
            logger.error(f"搜索关键词 '{keyword}' 的图片时出错: {str(e)}")
            continue
            
    return keyword_images

class ArticleTemplate:
    """文章模板"""
    def __init__(self, name, title_template, requirements_template):
        self.name = name
        self.title_template = title_template
        self.requirements_template = requirements_template

class GenerationProgress(QWidget):
    """生成进度组件"""
    cancel_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 标题栏
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("文章生成进度")
        title.setStyleSheet("""
            color: #E4E7ED;
            font-size: 16px;
            font-weight: bold;
        """)
        header_layout.addWidget(title)
        
        layout.addWidget(header)
        
        # 进度信息
        self.status_label = QLabel("准备开始生成文章...")
        self.status_label.setStyleSheet("""
            color: #C0C4CC;
            font-size: 14px;
            padding: 5px 0;
        """)
        layout.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2C2C2C;
                border: 1px solid #303030;
                border-radius: 4px;
                text-align: center;
                height: 20px;
                color: #E4E7ED;
            }
            QProgressBar::chunk {
                background-color: #409EFF;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # 取消按钮
        self.cancel_btn = AnimatedButton("取消生成")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F56C6C;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #F78989;
            }
        """)
        self.cancel_btn.clicked.connect(self.on_cancel_clicked)
        layout.addWidget(self.cancel_btn)
        
        # 添加阴影效果
        self.setGraphicsEffect(QGraphicsDropShadowEffect(
            blurRadius=10,
            xOffset=0,
            yOffset=2,
            color=QColor("#303030")
        ))
        
        # 设置背景色
        self.setStyleSheet("""
            QWidget {
                background-color: #1A1A1A;
                border: 1px solid #303030;
                border-radius: 4px;
                padding: 15px;
            }
        """)
        
    def on_cancel_clicked(self):
        """处理取消按钮点击事件"""
        self.cancel_signal.emit()
        self.hide()
        
    def update_progress(self, value, status):
        """更新进度"""
        self.progress_bar.setValue(value)
        self.status_label.setText(f"{status} ({value}%)")
        
        # 添加动画效果
        animation = QPropertyAnimation(self.progress_bar, b"value")
        animation.setDuration(300)
        animation.setStartValue(self.progress_bar.value())
        animation.setEndValue(value)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()

class TemplateSelector(QWidget):
    """模板选择器"""
    template_selected = pyqtSignal(ArticleTemplate)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.templates = [
            ArticleTemplate(
                "产品评测",
                "{产品名称}深度评测：优缺点全面分析",
                "请对{产品名称}进行全面评测，包括以下方面：\n1. 产品定位和特点\n2. 外观设计和做工\n3. 功能特性分析\n4. 使用体验\n5. 优缺点总结\n6. 购买建议"
            ),
            ArticleTemplate(
                "行业分析",
                "{行业名称}发展趋势分析：机遇与挑战",
                "请对{行业名称}进行深入分析，包括：\n1. 行业现状\n2. 市场规模\n3. 主要参与者\n4. 发展趋势\n5. 机遇与挑战\n6. 未来展望"
            ),
            ArticleTemplate(
                "教程指南",
                "{主题}完全指南：从入门到精通",
                "请编写一份关于{主题}的详细教程，包括：\n1. 基础概念介绍\n2. 核心要点讲解\n3. 实践步骤\n4. 常见问题解答\n5. 进阶技巧\n6. 资源推荐"
            )
        ]
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 标题栏
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("选择模板")
        title.setStyleSheet("""
            color: #303133;
            font-size: 16px;
            font-weight: bold;
        """)
        header_layout.addWidget(title)
        
        # 模板数量
        template_count = QLabel(f"{len(self.templates)} 个模板")
        template_count.setStyleSheet("""
            color: #909399;
            font-size: 14px;
        """)
        header_layout.addWidget(template_count)
        
        layout.addWidget(header)
        
        # 搜索框
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索模板...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #DCDFE6;
                border-radius: 4px;
                padding: 8px;
                color: #303133;
            }
            QLineEdit:focus {
                border-color: #409EFF;
            }
        """)
        self.search_input.textChanged.connect(self.filter_templates)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # 模板列表
        self.template_list = QListWidget()
        self.template_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #DCDFE6;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #EBEEF5;
                color: #303133;
            }
            QListWidget::item:selected {
                background-color: #ECF5FF;
                color: #409EFF;
            }
            QListWidget::item:hover {
                background-color: #F5F7FA;
            }
        """)
        
        for template in self.templates:
            item = QListWidgetItem(template.name)
            item.setToolTip(template.description)
            self.template_list.addItem(item)
        
        self.template_list.itemClicked.connect(self.on_template_selected)
        layout.addWidget(self.template_list)
        
        # 添加阴影效果
        self.setGraphicsEffect(QGraphicsDropShadowEffect(
            blurRadius=10,
            xOffset=0,
            yOffset=2,
            color=QColor("#DCDFE6")
        ))
    
    def filter_templates(self, text):
        """过滤模板"""
        self.template_list.clear()
        for template in self.templates:
            if text.lower() in template.name.lower() or text.lower() in template.description.lower():
                item = QListWidgetItem(template.name)
                item.setToolTip(template.description)
                self.template_list.addItem(item)
        
        # 添加淡入动画
        animation = QPropertyAnimation(self.template_list, b"windowOpacity")
        animation.setDuration(300)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.start()
    
    def on_template_selected(self, item):
        if item is None:
            return
        template = next(t for t in self.templates if t.name == item.text())
        self.template_selected.emit(template)
        
        # 添加点击动画
        animation = QPropertyAnimation(item, b"background")
        animation.setDuration(200)
        animation.setStartValue(QColor("#ECF5FF"))
        animation.setEndValue(QColor("#F5F7FA"))
        animation.start()

class ArticlePreview(QWidget):
    """文章预览组件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()
        self.connect_signals()
        self.save_clicked = False
        self.last_save_path = None  # 记录上次保存路径
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题栏
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("文章预览")
        title.setObjectName("nameLabel")
        title.setStyleSheet("""
            QLabel#nameLabel {
                color: #409EFF;
                font-size: 18px;
                font-weight: bold;
                padding-bottom: 4px;
            }
        """)
        header_layout.addWidget(title)
        
        # 字数统计
        self.word_count = QLabel("0 字")
        self.word_count.setObjectName("descLabel")
        self.word_count.setStyleSheet("""
            QLabel#descLabel {
                color: #C0C4CC;
                font-size: 14px;
                padding-bottom: 6px;
            }
        """)
        header_layout.addWidget(self.word_count)
        
        layout.addWidget(header)
        
        # 预览区域
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setStyleSheet("""
            QTextEdit {
                background-color: #2C2C2C;
                border: 1px solid #303030;
                border-radius: 4px;
                padding: 15px;
                font-family: "Microsoft YaHei", Arial, sans-serif;
                line-height: 1.6;
                font-size: 14px;
                color: #E4E7ED;
            }
            QTextEdit:focus {
                border-color: #409EFF;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2C2C2C;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #303030;
                border-radius: 3px;
                min-height: 15px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #606266;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        layout.addWidget(self.preview)
        
        # 操作按钮
        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        
        self.save_btn = AnimatedButton("保存文章")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #409EFF;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #66B1FF;
            }
            QPushButton:pressed {
                background-color: #3A8EE6;
            }
        """)
        buttons.addWidget(self.save_btn)
        
        layout.addLayout(buttons)
        
        # 设置卡片样式
        self.setStyleSheet("""
            QWidget {
                background-color: #1A1A1A;
                border: 1px solid #303030;
                border-radius: 4px;
                padding: 15px;
            }
            QWidget:hover {
                border-color: #409EFF;
            }
        """)
    
    def connect_signals(self):
        """连接信号"""
        self.save_btn.clicked.connect(self.save_article)
    
    def save_article(self):
        """保存文章"""
        try:
            # 检查main_window和article_result是否存在
            if not hasattr(self, 'main_window') or self.main_window is None:
                QMessageBox.warning(self, "警告", "无法访问主窗口")
                return
                
            if not hasattr(self.main_window, 'article_result') or self.main_window.article_result is None:
                QMessageBox.warning(self, "警告", "没有可保存的文章内容")
                return
            
            # 获取文章内容和文件ID
            article_content = self.main_window.article_result.get('article')
            file_id = self.main_window.article_result.get('file_id')
            
            if not article_content or not file_id:
                QMessageBox.warning(self, "警告", "文章内容不完整")
                return
            
            # 设置默认文件名
            default_filename = f"{file_id}.md"
            default_path = str(OUTPUT_DIR / default_filename)
            
            # 确保输出目录存在
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            # 检查文件是否已存在
            if os.path.exists(default_path):
                reply = QMessageBox.question(
                    self,
                    "确认覆盖",
                    "文件已存在，是否覆盖？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            # 检查磁盘空间
            try:
                required_space = len(article_content.encode('utf-8'))
                if not self.check_disk_space(default_path, required_space):
                    QMessageBox.critical(self, "错误", "磁盘空间不足")
                    return
            except Exception as e:
                # 继续保存，因为磁盘空间检查失败不是致命错误
                pass
            
            # 将文章内容写入文件，确保使用UTF-8编码
            try:
                with open(default_path, "w", encoding="utf-8") as f:
                    f.write(article_content)
                    logger.info(f"文章已保存到: {default_path}")
            except PermissionError:
                QMessageBox.critical(self, "错误", "没有写入权限")
                return
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
                return
            
            # 标记文章已保存
            self.save_clicked = True
            if hasattr(self.main_window, 'article_saved'):
                self.main_window.article_saved = True
            if hasattr(self.main_window, 'unsaved_changes'):
                self.main_window.unsaved_changes = False
            
            # 显示成功提示，包含保存位置
            QMessageBox.information(
                self, 
                "保存成功", 
                f"文章已保存到：\n{default_path}\n\n文件位置：\n{OUTPUT_DIR}"
            )
            
            # 更新状态栏
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(f"文章已保存到: {default_path}", 5000)
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存过程中发生错误: {str(e)}")
    
    def check_disk_space(self, file_path, required_space):
        """检查磁盘空间是否足够"""
        try:
            # 获取目标目录的磁盘空间
            drive = os.path.splitdrive(file_path)[0]
            free_space = psutil.disk_usage(drive).free
            
            # 预留10MB的缓冲空间
            buffer_space = 10 * 1024 * 1024
            return free_space > (required_space + buffer_space)
        except:
            return True  # 如果检查失败，默认返回True
    
    def update_content(self, content):
        """更新预览内容"""
        # 使用 markdown 解析器渲染内容，启用图片支持
        html_content = markdown.markdown(content, extensions=['markdown.extensions.tables'])
        
        # 添加基本的 HTML 样式
        styled_html = f"""
        <html>
        <head>
        <style>
            body {{
                font-family: "Microsoft YaHei", Arial, sans-serif;
                line-height: 1.6;
                color: #E4E7ED;
                padding: 10px;
            }}
            img {{
                max-width: 100%;
                height: auto;
                margin: 10px 0;
                border-radius: 4px;
            }}
            em {{
                color: #909399;
                font-style: italic;
            }}
            p {{
                margin: 10px 0;
            }}
        </style>
        </head>
        <body>
        {html_content}
        </body>
        </html>
        """
        
        self.preview.setHtml(styled_html)
        
        # 更新字数统计
        plain_text = self.preview.toPlainText()
        word_count = len(plain_text)
        self.word_count.setText(f"{word_count} 字")
        
        # 添加淡入动画
        animation = QPropertyAnimation(self.preview, b"windowOpacity")
        animation.setDuration(300)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.start()

class ArticleGeneratorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文章生成器")
        self.setMinimumSize(800, 600)
        self.current_view = "agents"
        
        # 初始化变量
        self.agents = []
        self.selected_agent = None
        self.article_result = None
        self.article_saved = False
        self.unsaved_changes = False
        self.generator = None
        self.cache_dir = CACHE_DIR  # 使用全局CACHE_DIR
        
        # 设置应用图标
        app_icon = get_app_icon()
        self.setWindowIcon(app_icon)
        
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(app_icon)
        self.tray_icon.setToolTip("文章生成器")
        
        # 创建托盘菜单
        tray_menu = QMenu()
        show_action = tray_menu.addAction("显示主窗口")
        show_action.triggered.connect(self.show)
        quit_action = tray_menu.addAction("退出")
        quit_action.triggered.connect(QApplication.quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # 初始化主题管理器
        self.theme_manager = ThemeManager()
        
        # 设置应用程序样式
        self.setStyleSheet(self.theme_manager.get_style('main_window'))
        
        # 加载智能体配置
        self.load_agents()
        self.setup_ui()
    
    def cleanup_resources(self):
        """清理资源"""
        # 删除所有缓存文件
        try:
            for cache_file in self.cache_dir.glob("*.md"):
                try:
                    cache_file.unlink()
                except Exception as e:
                    pass
        except Exception as e:
            pass
        
        # 清理其他资源
        if self.generator and self.generator.isRunning():
            self.generator.terminate()
            self.generator.wait()
        
        self.generator = None
        self.article_result = None
        self.article_saved = False
        self.unsaved_changes = False
        
        if hasattr(self, 'article_preview'):
            self.article_preview.save_clicked = False
            self.article_preview.last_save_path = None

    def closeEvent(self, event):
        """关闭主窗口时删除缓存文件并退出程序"""
        self.cleanup_resources()
        self.tray_icon.hide()
        event.accept()
        QApplication.quit()
            
    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(10)  # 减小间距
        layout.setContentsMargins(10, 10, 10, 10)  # 减小边距
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 5)  # 减小底部边距
        
        self.title_label = QLabel("文章生成器")
        self.title_label.setObjectName("headerLabel")
        self.title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header_layout.addWidget(self.title_label)
        
        self.add_agent_btn = QPushButton("添加智能体")
        self.add_agent_btn.setObjectName("addButton")
        self.add_agent_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_agent_btn.clicked.connect(self.show_add_agent)
        self.add_agent_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        header_layout.addWidget(self.add_agent_btn)
        
        layout.addWidget(header)
        
        # Main content area
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.content_area)
        
        self.show_agents_view()
    
    def show_agents_view(self):
        self.clear_content()
        self.current_view = "agents"
        self.title_label.setText("智能体列表")
        self.add_agent_btn.show()
        
        # 如果没有智能体，显示空状态
        if not self.agents:
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_layout.setContentsMargins(10, 10, 10, 10)
            
            empty_label = QLabel("还没有智能体")
            empty_label.setStyleSheet(f"""
                color: {self.theme_manager.current_theme['text_secondary']};
                font-size: 16px;
                margin: 10px;
            """)
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            
            add_btn = QPushButton("添加第一个智能体")
            add_btn.setStyleSheet(self.theme_manager.get_style('header'))
            add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            add_btn.clicked.connect(self.show_add_agent)
            add_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
            
            empty_layout.addStretch()
            empty_layout.addWidget(empty_label, alignment=Qt.AlignmentFlag.AlignCenter)
            empty_layout.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignCenter)
            empty_layout.addStretch()
            
            self.content_layout.addWidget(empty_widget)
            return
        
        # 创建网格布局来显示智能体卡片
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent;")
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        scroll_content = QWidget()
        grid_layout = QGridLayout(scroll_content)
        grid_layout.setSpacing(10)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # 固定每行显示3个卡片
        cards_per_row = 3
        
        # 添加智能体卡片到网格
        for i, agent in enumerate(self.agents):
            row = i // cards_per_row
            col = i % cards_per_row
            card = TemplateCard(agent, self)  # 传递主窗口引用
            card.setStyleSheet(self.theme_manager.get_style('card'))
            card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            
            # 设置对齐方式为左对齐和顶部对齐
            grid_layout.addWidget(card, row, col, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # 设置网格布局的对齐方式
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # 设置滚动区域的对齐方式
        scroll.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # 设置滚动区域的布局
        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 禁用水平滚动条
        
        # 设置主布局的对齐方式
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.content_layout.addWidget(scroll)
    
    def show_add_agent(self):
        self.clear_content()
        self.current_view = "add_agent"
        self.title_label.setText("添加智能体")
        self.add_agent_btn.hide()
        
        form = QWidget()
        form_layout = QFormLayout(form)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        self.agent_form = {
            'name': QLineEdit(),
            'purpose': QTextEdit(),
            'article_style': QTextEdit(),
            'expertise': QTextEdit(),
            'writing_style': QTextEdit()
        }
        
        # 设置占位符文本
        self.agent_form['name'].setPlaceholderText("请输入智能体名称（例如：科技评论家）")
        self.agent_form['purpose'].setPlaceholderText("请输入智能体的主要用途（例如：\n- 撰写科技产品评测\n- 分析行业发展趋势\n- 提供专业的技术见解）")
        self.agent_form['article_style'].setPlaceholderText("请输入文章风格（例如：\n- 专业严谨\n- 深入浅出\n- 数据驱动\n- 客观公正）")
        self.agent_form['expertise'].setPlaceholderText("请输入专业领域（例如：\n- 人工智能\n- 移动互联网\n- 消费电子\n- 科技创新）")
        self.agent_form['writing_style'].setPlaceholderText("请输入写作风格（例如：\n- 逻辑清晰\n- 语言生动\n- 观点鲜明\n- 案例丰富）")
        
        # 设置输入框的最小高度
        for field in ['purpose', 'article_style', 'expertise', 'writing_style']:
            self.agent_form[field].setMinimumHeight(100)
        
        form_layout.addRow("名称:", self.agent_form['name'])
        form_layout.addRow("用途:", self.agent_form['purpose'])
        form_layout.addRow("文章风格:", self.agent_form['article_style'])
        form_layout.addRow("专长:", self.agent_form['expertise'])
        form_layout.addRow("写作风格:", self.agent_form['writing_style'])
        
        buttons = QHBoxLayout()
        create_btn = QPushButton("创建智能体")
        create_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme_manager.current_theme['primary']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.theme_manager.current_theme['primary']};
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                background-color: {self.theme_manager.current_theme['primary']};
                opacity: 0.8;
            }}
        """)
        create_btn.clicked.connect(self.create_agent)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme_manager.current_theme['danger']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.theme_manager.current_theme['danger']};
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                background-color: {self.theme_manager.current_theme['danger']};
                opacity: 0.8;
            }}
        """)
        cancel_btn.clicked.connect(self.show_agents_view)
        
        buttons.addWidget(create_btn)
        buttons.addWidget(cancel_btn)
        form_layout.addRow(buttons)
        
        self.content_layout.addWidget(form)
    
    def show_article_view(self):
        if self.selected_agent is None:
            return
        self.clear_content()
        self.current_view = "article"
        self.title_label.setText(f"使用 {self.selected_agent.name} 生成文章")
        self.add_agent_btn.hide()
        
        # 创建分割布局
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: transparent;
            }
            QSplitter::handle:hover {
                background-color: #303030;
            }
        """)
        splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 左侧面板：文章生成控制
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        form = QWidget()
        form_layout = QFormLayout(form)
        form_layout.setSpacing(15)
        
        # 添加表单控件
        self.article_form = {}
        
        # 标题输入
        title_label = QLabel("文章标题")
        title_input = QLineEdit()
        title_input.setPlaceholderText("请输入文章标题")
        self.article_form['title'] = title_input
        form_layout.addRow(title_label, title_input)
        
        # 写作要求输入
        requirements_label = QLabel("写作要求")
        requirements_input = QTextEdit()
        requirements_input.setPlaceholderText("请输入写作要求（例如：\n1. 文章需要包含5个主要观点\n2. 每个观点都要有具体例子\n3. 使用轻松幽默的语言风格\n4. 结尾要给出行动建议）")
        requirements_input.setMinimumHeight(100)
        self.article_form['requirements'] = requirements_input
        form_layout.addRow(requirements_label, requirements_input)
        
        # 联网搜索开关
        web_search_label = QLabel("启用联网搜索")
        web_search_checkbox = QCheckBox()
        web_search_checkbox.setChecked(True)
        self.article_form['enable_web_search'] = web_search_checkbox
        form_layout.addRow(web_search_label, web_search_checkbox)
        
        # 生成和取消按钮
        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        
        generate_btn = QPushButton("生成文章")
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #409EFF;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #66B1FF;
            }
            QPushButton:pressed {
                background-color: #3A8EE6;
            }
        """)
        generate_btn.clicked.connect(self.generate_article)
        
        cancel_btn = QPushButton("返回")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F56C6C;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #F78989;
            }
            QPushButton:pressed {
                background-color: #E64C4C;
            }
        """)
        cancel_btn.clicked.connect(self.back_to_agents)
        
        buttons.addWidget(generate_btn)
        buttons.addWidget(cancel_btn)
        form_layout.addRow(buttons)
        
        # 设置表单样式
        form.setStyleSheet("""
            QWidget {
                background-color: #1A1A1A;
                border: 1px solid #303030;
                border-radius: 4px;
                padding: 15px;
            }
            QLabel {
                color: #E4E7ED;
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit, QTextEdit {
                background-color: #2C2C2C;
                border: 1px solid #303030;
                border-radius: 4px;
                padding: 8px;
                color: #E4E7ED;
                font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #409EFF;
            }
            QCheckBox {
                color: #E4E7ED;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #303030;
                background-color: #2C2C2C;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #409EFF;
                background-color: #409EFF;
                border-radius: 3px;
            }
        """)
        form.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        left_layout.addWidget(form)
        
        # 添加生成进度组件
        self.progress_widget = GenerationProgress()
        self.progress_widget.setStyleSheet("""
            QWidget {
                background-color: #1A1A1A;
                border: 1px solid #303030;
                border-radius: 4px;
                padding: 15px;
            }
            QLabel {
                color: #E4E7ED;
                font-size: 14px;
            }
            QProgressBar {
                background-color: #2C2C2C;
                border: 1px solid #303030;
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #409EFF;
                border-radius: 4px;
            }
        """)
        self.progress_widget.hide()
        self.progress_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        left_layout.addWidget(self.progress_widget)
        
        splitter.addWidget(left_panel)
        
        # 右侧面板：文章预览
        self.article_preview = ArticlePreview(self)
        self.article_preview.setStyleSheet("""
            QWidget {
                background-color: #1A1A1A;
                border: 1px solid #303030;
                border-radius: 4px;
                padding: 15px;
            }
            QLabel#nameLabel {
                color: #409EFF;
                font-size: 18px;
                font-weight: bold;
                padding-bottom: 4px;
            }
            QLabel#descLabel {
                color: #C0C4CC;
                font-size: 14px;
                padding-bottom: 6px;
            }
            QTextEdit {
                background-color: #2C2C2C;
                border: 1px solid #303030;
                border-radius: 4px;
                padding: 15px;
                font-family: "Microsoft YaHei", Arial, sans-serif;
                line-height: 1.6;
                font-size: 14px;
                color: #E4E7ED;
            }
            QTextEdit:focus {
                border-color: #409EFF;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2C2C2C;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #303030;
                border-radius: 3px;
                min-height: 15px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #606266;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QPushButton {
                background-color: #409EFF;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #66B1FF;
            }
            QPushButton:pressed {
                background-color: #3A8EE6;
            }
        """)
        self.article_preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        splitter.addWidget(self.article_preview)
        
        # 设置分割比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        self.content_layout.addWidget(splitter)
        
        # 检查是否有缓存文件
        if self.cache_dir.exists():
            # 获取所有缓存文件
            cache_files = list(self.cache_dir.glob("*.md"))
            if cache_files:
                # 按文件名中的时间戳排序（最新的在前）
                cache_files.sort(key=lambda x: x.stem.split('-')[-1], reverse=True)
                # 读取最新的缓存文件
                try:
                    with open(cache_files[0], "r", encoding="utf-8") as f:
                        cached_content = f.read()
                        # 更新预览
                        self.article_preview.update_content(cached_content)
                        # 更新article_result
                        self.article_result = {
                            'file_id': cache_files[0].stem,
                            'article': cached_content
                        }
                except Exception as e:
                    logger.error(f"Error reading cache file: {str(e)}")
                    # 如果读取缓存失败，使用内存中的内容
                    if self.article_result and self.article_result.get('article'):
                        self.article_preview.update_content(self.article_result['article'])
    
    def clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    def load_agents(self):
        """加载所有智能体"""
        self.agents = Agent.list_all()
            
    def create_agent(self):
        """创建新智能体"""
        # 验证表单
        if not self.agent_form['name'].text().strip():
            QMessageBox.warning(self, "警告", "名称不能为空")
            return
        if not self.agent_form['purpose'].toPlainText().strip():
            QMessageBox.warning(self, "警告", "用途不能为空")
            return
        if not self.agent_form['article_style'].toPlainText().strip():
            QMessageBox.warning(self, "警告", "文章风格不能为空")
            return
        if not self.agent_form['expertise'].toPlainText().strip():
            QMessageBox.warning(self, "警告", "专长不能为空")
            return
        if not self.agent_form['writing_style'].toPlainText().strip():
            QMessageBox.warning(self, "警告", "写作风格不能为空")
            return
        
        agent_data = {
            'name': self.agent_form['name'].text(),
            'purpose': self.agent_form['purpose'].toPlainText(),
            'article_style': self.agent_form['article_style'].toPlainText(),
            'expertise': self.agent_form['expertise'].toPlainText(),
            'writing_style': self.agent_form['writing_style'].toPlainText()
        }
        
        # 检查是否存在同名智能体
        if any(agent.name == agent_data['name'] for agent in self.agents):
            QMessageBox.warning(self, "警告", "已存在同名智能体")
            return
        
        # 创建并保存智能体
        agent = Agent(**agent_data)
        
        try:
            agent.save()
            self.load_agents()  # 重新加载智能体列表
            
            # 显示成功提示
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("成功")
            msg.setText("智能体创建成功")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            
            self.show_agents_view()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建智能体失败: {str(e)}")
    
    def use_agent(self, agent):
        if agent is None:
            return
        self.selected_agent = agent
        self.show_article_view()
        
    def generate_article(self):
        if self.selected_agent is None:
            QMessageBox.warning(self, "警告", "请先选择一个智能体")
            return
        # 验证表单
        if not self.article_form['title'].text().strip():
            QMessageBox.warning(self, "警告", "标题不能为空")
            return
        if not self.article_form['requirements'].toPlainText().strip():
            QMessageBox.warning(self, "警告", "写作要求不能为空")
            return
        
        title = self.article_form['title'].text().strip()
        requirements = self.article_form['requirements'].toPlainText().strip()
        enable_web_search = self.article_form['enable_web_search'].isChecked()
        
        # 显示进度组件
        self.progress_widget.show()
        self.progress_widget.update_progress(0, "准备生成...")
        
        # 创建文章生成器线程
        self.generator = ArticleGenerator(
            title,
            requirements,
            self.selected_agent,
            enable_web_search
        )
        
        # 连接信号
        self.generator.progress.connect(self.handle_generation_progress)
        self.generator.finished.connect(self.handle_generation_complete)
        self.generator.error.connect(self.handle_generation_error)
        self.progress_widget.cancel_signal.connect(self.cancel_generation)  # 连接取消信号
        
        # 启动生成
        self.generator.start()
    
    def cancel_generation(self):
        """取消文章生成"""
        if self.generator and self.generator.isRunning():
            self.generator.terminate()  # 终止线程
            self.generator.wait()  # 等待线程结束
            self.progress_widget.hide()
            QMessageBox.information(self, "提示", "已取消文章生成")
    
    def handle_generation_progress(self, status, progress):
        """处理生成进度"""
        self.progress_widget.update_progress(progress, status)
    
    def handle_generation_complete(self, result):
        """处理生成完成"""
        self.article_result = result
        self.article_saved = False
        self.unsaved_changes = True
        
        # 保存到缓存
        try:
            cache_file = self.cache_dir / f"{result['file_id']}.md"
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(result['article'])
        except Exception as e:
            logger.error(f"Error saving to cache: {str(e)}")
        
        # 更新预览
        self.progress_widget.update_progress(100, "生成完成")
        self.article_preview.update_content(result['article'])
        self.progress_widget.hide()
        
        # 更新状态栏
        self.statusBar().showMessage("文章生成完成，请保存", 5000)
    
    def handle_generation_error(self, error_msg):
        """处理生成错误"""
        self.progress_widget.update_progress(0, "生成失败")
        
        # 创建错误对话框
        error_dialog = QMessageBox(self)
        error_dialog.setWindowTitle("文章生成失败")
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        
        # 设置错误信息
        error_dialog.setText("文章生成过程中发生错误")
        
        # 添加详细错误信息
        error_dialog.setInformativeText(f"错误详情：\n{error_msg}")
        
        # 添加重试按钮
        error_dialog.addButton("重试", QMessageBox.ButtonRole.AcceptRole)
        error_dialog.addButton("取消", QMessageBox.ButtonRole.RejectRole)
        
        # 显示对话框并获取用户选择
        result = error_dialog.exec()
        
        if result == QMessageBox.ButtonRole.AcceptRole:
            # 用户选择重试，重新开始生成
            self.generate_article()
        else:
            # 用户选择取消，隐藏进度条
            self.progress_widget.hide()
            
    def back_to_agents(self):
        """返回代理列表"""
        # 直接返回智能体列表视图
        self.show_agents_view()

    def delete_agent(self, agent: Agent):
        """删除智能体"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除智能体 {agent.name} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                agent.delete()
                self.load_agents()  # 重新加载智能体列表
                self.show_agents_view()
                QMessageBox.information(self, "成功", "智能体删除成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除智能体失败: {str(e)}")

    def apply_template(self, template):
        if template is None or not hasattr(self, 'article_form'):
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("填写模板参数")
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        # 提取模板参数
        params = []
        for match in re.finditer(r'\{([^}]+)\}', template.title_template + template.requirements_template):
            param = match.group(1)
            if param not in params:
                params.append(param)
        
        # 创建参数输入框
        param_inputs = {}
        for param in params:
            label = QLabel(f"{param}:")
            input_field = QLineEdit()
            layout.addWidget(label)
            layout.addWidget(input_field)
            param_inputs[param] = input_field
        
        # 确定按钮
        buttons = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 替换模板参数
            title = template.title_template
            requirements = template.requirements_template
            
            for param, input_field in param_inputs.items():
                value = input_field.text()
                title = title.replace(f"{{{param}}}", value)
                requirements = requirements.replace(f"{{{param}}}", value)
            
            # 更新表单
            self.article_form['title'].setText(title)
            self.article_form['requirements'].setText(requirements)
            
            # 切换到文章生成界面
            self.show_article_view()

    def edit_agent(self, agent):
        """编辑智能体"""
        self.clear_content()
        self.current_view = "edit_agent"
        self.title_label.setText(f"编辑智能体: {agent.name}")
        self.add_agent_btn.hide()
        
        form = QWidget()
        form_layout = QFormLayout(form)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        self.agent_form = {
            'name': QLineEdit(agent.name),
            'purpose': QTextEdit(agent.purpose),
            'article_style': QTextEdit(agent.article_style),
            'expertise': QTextEdit(agent.expertise),
            'writing_style': QTextEdit(agent.writing_style)
        }
        
        # 设置表单样式
        form.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme_manager.current_theme['card']};
                border: 1px solid {self.theme_manager.current_theme['border']};
                border-radius: 4px;
                padding: 15px;
            }}
            QLabel {{
                color: {self.theme_manager.current_theme['text']};
                font-size: 14px;
                font-weight: bold;
            }}
            QLineEdit, QTextEdit {{
                background-color: {self.theme_manager.current_theme['background']};
                border: 1px solid {self.theme_manager.current_theme['border']};
                border-radius: 4px;
                padding: 8px;
                color: {self.theme_manager.current_theme['text']};
                font-size: 14px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border-color: {self.theme_manager.current_theme['primary']};
            }}
        """)
        
        form_layout.addRow("名称:", self.agent_form['name'])
        form_layout.addRow("用途:", self.agent_form['purpose'])
        form_layout.addRow("文章风格:", self.agent_form['article_style'])
        form_layout.addRow("专长:", self.agent_form['expertise'])
        form_layout.addRow("写作风格:", self.agent_form['writing_style'])
        
        buttons = QHBoxLayout()
        save_btn = QPushButton("保存修改")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme_manager.current_theme['primary']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.theme_manager.current_theme['primary']};
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                background-color: {self.theme_manager.current_theme['primary']};
                opacity: 0.8;
            }}
        """)
        save_btn.clicked.connect(lambda: self.save_agent_edit(agent))
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme_manager.current_theme['danger']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.theme_manager.current_theme['danger']};
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                background-color: {self.theme_manager.current_theme['danger']};
                opacity: 0.8;
            }}
        """)
        cancel_btn.clicked.connect(self.show_agents_view)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        form_layout.addRow(buttons)
        
        self.content_layout.addWidget(form)
        
    def save_agent_edit(self, original_agent):
        """保存智能体修改"""
        # 验证表单
        if not self.agent_form['name'].text().strip():
            QMessageBox.warning(self, "警告", "名称不能为空")
            return
        if not self.agent_form['purpose'].toPlainText().strip():
            QMessageBox.warning(self, "警告", "用途不能为空")
            return
        if not self.agent_form['article_style'].toPlainText().strip():
            QMessageBox.warning(self, "警告", "文章风格不能为空")
            return
        if not self.agent_form['expertise'].toPlainText().strip():
            QMessageBox.warning(self, "警告", "专长不能为空")
            return
        if not self.agent_form['writing_style'].toPlainText().strip():
            QMessageBox.warning(self, "警告", "写作风格不能为空")
            return
        
        # 检查是否存在同名智能体（排除当前编辑的智能体）
        new_name = self.agent_form['name'].text().strip()
        if new_name != original_agent.name and any(agent.name == new_name for agent in self.agents):
            QMessageBox.warning(self, "警告", "已存在同名智能体")
            return
        
        # 更新智能体信息
        original_agent.name = new_name
        original_agent.purpose = self.agent_form['purpose'].toPlainText().strip()
        original_agent.article_style = self.agent_form['article_style'].toPlainText().strip()
        original_agent.expertise = self.agent_form['expertise'].toPlainText().strip()
        original_agent.writing_style = self.agent_form['writing_style'].toPlainText().strip()
        original_agent.updated_at = datetime.now()
        
        try:
            # 如果名称改变，需要删除旧文件
            if new_name != original_agent.name:
                original_agent.delete()
            
            # 保存新文件
            original_agent.save()
            self.load_agents()  # 重新加载智能体列表
            
            # 显示成功提示
            QMessageBox.information(self, "成功", "智能体修改成功")
            self.show_agents_view()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"修改智能体失败: {str(e)}")

    def cleanup_resources(self):
        """清理资源"""
        # 删除所有缓存文件
        try:
            for cache_file in self.cache_dir.glob("*.md"):
                try:
                    cache_file.unlink()
                except Exception as e:
                    pass
        except Exception as e:
            pass
        
        # 清理其他资源
        if self.generator and self.generator.isRunning():
            self.generator.terminate()
            self.generator.wait()
        
        self.generator = None
        self.article_result = None
        self.article_saved = False
        self.unsaved_changes = False
        
        if hasattr(self, 'article_preview'):
            self.article_preview.save_clicked = False
            self.article_preview.last_save_path = None

    def setup_system_tray(self):
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(get_app_icon())
        
        # 创建托盘菜单
        tray_menu = QMenu()
        show_action = tray_menu.addAction("显示主窗口")
        show_action.triggered.connect(self.show)
        
        exit_action = tray_menu.addAction("退出")
        exit_action.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def quit_application(self):
        """退出应用程序"""
        self.cleanup_resources()
        self.tray_icon.hide()
        QApplication.quit()

class TemplateCard(QFrame):
    """智能体卡片"""
    def __init__(self, agent, parent=None):
        super().__init__(parent)
        self.agent = agent
        self.main_window = parent  # 保存主窗口引用
        self.setup_ui()
    
    def setup_ui(self):
        self.setObjectName("agentCard")
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        
        # 设置固定大小
        self.setFixedWidth(250)
        self.setMinimumHeight(200)
        
        # 创建表单布局
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # 名称行
        name_label = QLabel("名称:")
        name_label.setObjectName("fieldLabel")
        name_label.setStyleSheet("""
            QLabel#fieldLabel {
                color: #909399;
                font-size: 13px;
            }
            QLabel#fieldLabel:hover {
                border: none;
            }
        """)
        
        name_value = QLabel(self.agent.name)
        name_value.setObjectName("nameLabel")
        name_value.setStyleSheet("""
            QLabel#nameLabel {
                color: #409EFF;
                font-size: 14px;
                font-weight: bold;
            }
            QLabel#nameLabel:hover {
                border: none;
            }
        """)
        form_layout.addRow(name_label, name_value)
        
        # 用途行
        purpose_label = QLabel("用途:")
        purpose_label.setObjectName("fieldLabel")
        purpose_label.setStyleSheet("""
            QLabel#fieldLabel {
                color: #909399;
                font-size: 13px;
            }
            QLabel#fieldLabel:hover {
                border: none;
            }
        """)
        
        purpose_value = QLabel(self.agent.purpose)
        purpose_value.setObjectName("purposeLabel")
        purpose_value.setWordWrap(True)
        purpose_value.setStyleSheet("""
            QLabel#purposeLabel {
                color: #C0C4CC;
                font-size: 13px;
                line-height: 1.4;
            }
            QLabel#purposeLabel:hover {
                border: none;
            }
        """)
        purpose_value.setMaximumHeight(80)
        form_layout.addRow(purpose_label, purpose_value)
        
        # 文章风格行
        style_label = QLabel("文章风格:")
        style_label.setObjectName("fieldLabel")
        style_label.setStyleSheet("""
            QLabel#fieldLabel {
                color: #909399;
                font-size: 13px;
            }
            QLabel#fieldLabel:hover {
                border: none;
            }
        """)
        
        style_value = QLabel(self.agent.article_style)
        style_value.setObjectName("styleLabel")
        style_value.setWordWrap(True)
        style_value.setStyleSheet("""
            QLabel#styleLabel {
                color: #C0C4CC;
                font-size: 13px;
                line-height: 1.4;
            }
            QLabel#styleLabel:hover {
                border: none;
            }
        """)
        style_value.setMaximumHeight(80)
        form_layout.addRow(style_label, style_value)
        
        # 将表单布局添加到主布局
        main_layout.addLayout(form_layout)
        
        # 添加弹性空间，将按钮推到底部
        main_layout.addStretch()
        
        # 创建按钮容器
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(15)  # 按钮之间的间距
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 左侧按钮（使用此模板）
        use_btn = QPushButton("使用此模板")
        use_btn.setFixedSize(100, 28)  # 调整按钮大小
        use_btn.setStyleSheet("""
            QPushButton {
                background-color: #409EFF;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #66B1FF;
            }
            QPushButton:pressed {
                background-color: #3A8EE6;
            }
        """)
        use_btn.clicked.connect(self.on_use_clicked)
        button_layout.addWidget(use_btn)
        
        # 右侧按钮（修改）
        edit_btn = QPushButton("修改")
        edit_btn.setFixedSize(40, 28)  # 调整按钮大小，确保比文字大一点
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #E6A23C;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
                padding: 0px;
                margin-left: 0px;
                min-width: 30px;
            }
            QPushButton:hover {
                background-color: #EBB563;
            }
            QPushButton:pressed {
                background-color: #CF9236;
            }
        """)
        edit_btn.clicked.connect(self.on_edit_clicked)
        button_layout.addWidget(edit_btn)
        
        # 添加删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.setFixedSize(40, 28)  # 调整按钮大小，确保比文字大一点
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #F56C6C;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
                padding: 0px;
                margin-left: 0px;
                min-width: 30px;
            }
            QPushButton:hover {
                background-color: #F78989;
            }
            QPushButton:pressed {
                background-color: #E64C4C;
            }
        """)
        delete_btn.clicked.connect(self.on_delete_clicked)
        button_layout.addWidget(delete_btn)
        
        # 将按钮容器添加到主布局
        main_layout.addWidget(button_container)
        
        # 设置卡片样式
        self.setStyleSheet("""
            QFrame#agentCard {
                background-color: #1A1A1A;
                border: 1px solid #303030;
                border-radius: 4px;
                padding: 12px;
            }
            QFrame#agentCard:hover {
                border: 1px solid #303030;
            }
        """)
    
    def on_use_clicked(self):
        """处理使用按钮点击事件"""
        if self.main_window:
            self.main_window.use_agent(self.agent)
            
    def on_edit_clicked(self):
        """处理修改按钮点击事件"""
        if self.main_window:
            self.main_window.edit_agent(self.agent)
            
    def on_delete_clicked(self):
        """处理删除按钮点击事件"""
        if self.main_window:
            self.main_window.delete_agent(self.agent)

class ImageSearcher:
    def __init__(self):
        self.session = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.baidu.com/"
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def crawl_baike_images(self, query: str, context: str = None) -> List[str]:
        """从百度百科爬取图片"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # 1. 先搜索词条
                search_url = f"https://baike.baidu.com/search?word={urllib.parse.quote(query)}"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Referer': 'https://baike.baidu.com/',
                    'Connection': 'keep-alive'
                }
                
                async with self.session.get(search_url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # 2. 获取搜索结果链接
                        results = soup.find_all('a', class_='result-title')
                        if not results:
                            logger.warning(f"未找到相关词条: {query}")
                            return []
                            
                        # 3. 访问每个词条页面获取图片
                        images = []
                        for result in results[:3]:  # 最多访问前3个词条
                            entry_url = 'https://baike.baidu.com' + result['href']
                            try:
                                async with self.session.get(entry_url, headers=headers, timeout=10) as entry_response:
                                    if entry_response.status == 200:
                                        entry_html = await entry_response.text()
                                        entry_soup = BeautifulSoup(entry_html, 'html.parser')
                                        
                                        # 4. 获取词条图片
                                        # 4.1 获取主图
                                        main_image = entry_soup.find('div', class_='summary-pic')
                                        if main_image:
                                            img = main_image.find('img')
                                            if img and img.get('src'):
                                                img_url = img['src']
                                                if not img_url.startswith('http'):
                                                    img_url = 'https:' + img_url if img_url.startswith('//') else 'https://baike.baidu.com' + img_url
                                                images.append(img_url)
                                        
                                        # 4.2 获取内容中的图片
                                        content = entry_soup.find('div', class_='main-content')
                                        if content:
                                            for img in content.find_all('img'):
                                                if img.get('src'):
                                                    img_url = img['src']
                                                    if not img_url.startswith('http'):
                                                        img_url = 'https:' + img_url if img_url.startswith('//') else 'https://baike.baidu.com' + img_url
                                                    images.append(img_url)
                                        
                                        # 4.3 获取图库中的图片
                                        gallery = entry_soup.find('div', class_='album-list')
                                        if gallery:
                                            for img in gallery.find_all('img'):
                                                if img.get('src'):
                                                    img_url = img['src']
                                                    if not img_url.startswith('http'):
                                                        img_url = 'https:' + img_url if img_url.startswith('//') else 'https://baike.baidu.com' + img_url
                                                    images.append(img_url)
                            except Exception as e:
                                logger.error(f"访问词条页面失败: {str(e)}")
                                continue
                        
                        # 5. 过滤和清理图片URL
                        valid_images = []
                        for img_url in set(images):
                            # 移除URL中的转义字符
                            img_url = img_url.replace('\\', '')
                            # 确保URL是有效的
                            if img_url.startswith('http') and any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                                valid_images.append(img_url)
                        
                        if valid_images:
                            logger.info(f"从百度百科获取到 {len(valid_images)} 张图片")
                            return valid_images[:8]  # 返回前8张图片
                        else:
                            logger.warning("未从百度百科找到图片")
                            return []
                            
                    else:
                        logger.warning(f"百度百科搜索失败，状态码: {response.status}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay)
                            continue
                        
            except Exception as e:
                logger.error(f"爬取百度百科图片失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                
        return []

    async def crawl_baidu_images(self, query: str, context: str = None) -> List[str]:
        """从百度图片搜索图片"""
        try:
            # 1. 构建搜索URL
            encoded_query = urllib.parse.quote(query)
            url = f"https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&is=&fp=result&queryWord={encoded_query}&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=-1&z=&ic=0&hd=&latest=&copyright=&word={encoded_query}&s=&se=&tab=&width=&height=&face=0&istype=2&qc=&nc=1&fr=&expermode=&force=&pn=0&rn=30&gsm=1e&{int(time.time()*1000)}="
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://image.baidu.com/',
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
            }
            
            # 2. 发送请求获取图片数据
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    logger.error(f"百度图片API请求失败: {response.status}")
                    return []
                
                # 3. 解析响应数据
                try:
                    data = await response.json()
                    if not data or 'data' not in data:
                        logger.error("百度图片API返回数据格式错误")
                        return []
                    
                    # 4. 提取图片URL
                    image_urls = set()
                    for item in data['data']:
                        if not item:
                            continue
                        
                        # 尝试获取不同质量的图片URL
                        urls_to_try = [
                            item.get('middleURL'),  # 中等质量
                            item.get('thumbURL'),   # 缩略图
                            item.get('objURL'),     # 原始图片
                            item.get('hoverURL')    # 悬停图片
                        ]
                        
                        for url in urls_to_try:
                            if not url:
                                continue
                            
                            # 清理URL
                            url = url.replace('\\/', '/')
                            url = url.replace('\\u002F', '/')
                            url = url.replace('\\u003D', '=')
                            url = url.replace('\\u0026', '&')
                            
                            # 检查URL格式
                            if not url.startswith('http'):
                                continue
                            
                            # 检查图片格式
                            if not any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                                continue
                            
                            # 检查图片质量
                            try:
                                if await check_image_quality(url):
                                    image_urls.add(url)
                                    break  # 找到一个可用URL就停止
                            except:
                                continue
                    
                    # 5. 检查图片相关性
                    relevant_urls = []
                    for url in image_urls:
                        try:
                            if await check_image_relevance(url, query, context):
                                relevant_urls.append(url)
                                if len(relevant_urls) >= 10:  # 最多返回10个相关图片
                                    break
                        except Exception as e:
                            logger.error(f"检查图片相关性时出错: {str(e)}")
                            continue
                    
                    if relevant_urls:
                        logger.info(f"成功获取到 {len(relevant_urls)} 张相关图片")
                        return relevant_urls
                    else:
                        logger.warning("未找到相关图片，返回所有有效图片")
                        return list(image_urls)[:10]  # 如果没有相关图片，返回前10个有效图片
                        
                except json.JSONDecodeError:
                    logger.error("百度图片API返回数据解析失败")
                    return []
                
        except Exception as e:
            logger.error(f"爬取百度图片时出错: {str(e)}")
            return []

    async def crawl_unsplash_images(self, query: str, context: str = None) -> List[str]:
        """从Unsplash爬取图片"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # 1. 构建搜索URL
                encoded_query = urllib.parse.quote(query)
                url = f"https://unsplash.com/s/photos/{encoded_query}"
                
                # 2. 添加Unsplash特定的请求头
                headers = {
                    **self.headers,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Cache-Control': 'max-age=0',
                    'Connection': 'keep-alive',
                    'Host': 'unsplash.com',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                # 3. 发送请求
                async with self.session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        images = []
                        
                        # 4. 从HTML中提取图片URL
                        # 4.1 从图片网格中提取
                        image_grid = soup.find('div', class_='masonry')
                        if image_grid:
                            for img in image_grid.find_all('img'):
                                if img.get('src'):
                                    img_url = img['src']
                                    if not img_url.startswith('http'):
                                        img_url = 'https:' + img_url if img_url.startswith('//') else 'https://unsplash.com' + img_url
                                    images.append(img_url)
                        
                        # 4.2 从图片列表中提取
                        image_list = soup.find('div', class_='photo-list')
                        if image_list:
                            for img in image_list.find_all('img'):
                                if img.get('src'):
                                    img_url = img['src']
                                    if not img_url.startswith('http'):
                                        img_url = 'https:' + img_url if img_url.startswith('//') else 'https://unsplash.com' + img_url
                                    images.append(img_url)
                        
                        # 4.3 从图片详情页获取高清图片
                        if not images:
                            # 获取图片详情页链接
                            detail_links = []
                            for a in soup.find_all('a', class_='photo-link'):
                                if a.get('href'):
                                    detail_links.append(a['href'])
                            
                            # 访问详情页获取高清图片
                            for link in detail_links[:5]:  # 限制访问数量
                                try:
                                    if not link.startswith('http'):
                                        link = 'https://unsplash.com' + link
                                    async with self.session.get(link, headers=headers, timeout=5) as detail_response:
                                        if detail_response.status == 200:
                                            detail_html = await detail_response.text()
                                            detail_soup = BeautifulSoup(detail_html, 'html.parser')
                                            hd_img = detail_soup.find('img', class_='photo')
                                            if hd_img and hd_img.get('src'):
                                                images.append(hd_img['src'])
                                except Exception as e:
                                    logger.error(f"访问详情页失败: {str(e)}")
                        
                        return list(set(images))
                    else:
                        logger.warning(f"Unsplash图片请求失败，状态码: {response.status}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay)
                            continue
                        
            except Exception as e:
                logger.error(f"爬取Unsplash图片失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                
        return []
        
    async def search_images(self, query: str, context: str = None) -> List[str]:
        """搜索图片，按顺序尝试多个来源"""
        images = []
        
        # 1. 尝试百度百科
        logger.info(f"正在从百度百科爬取关键词 '{query}' 的图片...")
        baike_images = await self.crawl_baike_images(query, context)
        if baike_images:
            return baike_images
            
        # 2. 尝试百度图片
        logger.info(f"百度百科未找到合适图片，正在从百度图片爬取关键词 '{query}' 的图片...")
        baidu_images = await self.crawl_baidu_images(query, context)
        if baidu_images:
            return baidu_images
            
        # 3. 尝试必应图片
        logger.info(f"百度图片未找到合适图片，正在从必应图片爬取关键词 '{query}' 的图片...")
        bing_images = await self.crawl_bing_images(query, context)
        if bing_images:
            return bing_images
            
        # 4. 尝试Unsplash
        logger.info(f"必应图片未找到合适图片，正在从Unsplash爬取关键词 '{query}' 的图片...")
        unsplash_images = await self.crawl_unsplash_images(query, context)
        if unsplash_images:
            return unsplash_images
            
        logger.warning(f"未能找到关键词 '{query}' 的合适图片")
        return []

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ArticleGeneratorApp()
    window.show()
    sys.exit(app.exec()) 