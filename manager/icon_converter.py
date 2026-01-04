# -*- coding: utf-8 -*-
"""
图标转换工具
支持 Emoji 转 ICO 和 图片 转 ICO
"""

import os
import hashlib
import requests
from PIL import Image
from io import BytesIO


class IconConverter:
    """图标转换工具"""

    def __init__(self, cache_dir=None):
        """
        初始化转换器

        Args:
            cache_dir: 图标缓存目录，如果为 None 则不缓存
        """
        self.cache_dir = cache_dir
        self.ico_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        self.twemoji_base = "https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.0.3/assets/72x72/"

        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _save_ico(self, img, save_path):
        """保存图片为 ICO"""
        # Ensure image is RGBA
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        img.save(save_path, format='ICO', sizes=self.ico_sizes)
        return save_path

    def _emoji_to_twicode(self, emoji):
        """将 Emoji 转换为 Twemoji 文件名"""
        codepoints = [f"{ord(c):x}" for c in emoji]
        return "-".join(codepoints)

    def _download_emoji_image(self, emoji):
        """从 Twemoji CDN 下载 Emoji 图片"""
        twemoji_filename = self._emoji_to_twicode(emoji)
        url = f"{self.twemoji_base}{twemoji_filename}.png"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            img = Image.open(BytesIO(response.content))
            # Resize to largest size needed
            img = img.convert("RGBA").resize((256, 256), Image.Resampling.LANCZOS)

            return img
        except Exception as e:
            print(f"下载 Emoji 失败: {e}")
            raise Exception(f"无法下载 Emoji 图片: {e}")

    def convert_emoji(self, emoji, folder_path=None):
        """
        将 Emoji 转换为 .ico 文件

        Args:
            emoji: Emoji 字符
            folder_path: 目标文件夹路径 (用于非缓存模式)
        """
        if not emoji or not isinstance(emoji, str) or not emoji.strip():
            raise ValueError("Invalid emoji input")

        if len(emoji) == 1:
            emoji_code = hex(ord(emoji))[2:]
        else:
            emoji_hash = hashlib.md5(emoji.encode('utf-8')).hexdigest()[:8]
            emoji_code = f"combo_{emoji_hash}"

        ico_filename = f".folder_{emoji_code}.ico"

        if self.cache_dir:
            ico_path = os.path.join(self.cache_dir, ico_filename)
        elif folder_path:
            ico_path = os.path.join(folder_path, ico_filename)
        else:
            raise ValueError("Either cache_dir or folder_path must be provided")

        if os.path.exists(ico_path):
            return ico_path

        img = self._download_emoji_image(emoji)
        return self._save_ico(img, ico_path)

    def convert_from_file(self, source_path):
        """
        将本地图片转换为 .ico 文件
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"File not found: {source_path}")

        # Validate file extension
        valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.webp'}
        ext = os.path.splitext(source_path)[1].lower()
        if ext not in valid_extensions:
            raise ValueError(f"Unsupported file type: {ext}. Supported types: {', '.join(valid_extensions)}")

        with open(source_path, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()[:8]
            
        ico_filename = f"custom_{file_hash}.ico"
        
        if self.cache_dir:
            ico_path = os.path.join(self.cache_dir, ico_filename)
        else:
            # Default to same directory as source
            base_dir = os.path.dirname(source_path)
            ico_path = os.path.join(base_dir, ico_filename)

        if not os.path.exists(ico_path):
            try:
                with Image.open(source_path) as img:
                    self._save_ico(img, ico_path)
            except Exception as e:
                # Clean up if partial file was created
                if os.path.exists(ico_path):
                    try:
                        os.remove(ico_path)
                    except:
                        pass
                raise ValueError(f"Invalid image file or conversion failed: {e}")
            
        return ico_path
