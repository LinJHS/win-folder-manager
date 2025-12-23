# -*- coding: utf-8 -*-
"""
Emoji 转 ICO 工具
将 AI 生成的 Emoji 转换为 Windows 文件夹图标文件
使用 Twemoji CDN 获取高质量彩色 Emoji 图片
"""

import os
import hashlib
import requests
from PIL import Image


class EmojiConverter:
    """Emoji 转 ICO 工具"""

    def __init__(self, cache_dir=None):
        """
        初始化转换器

        Args:
            cache_dir: Emoji 缓存目录，如果为 None 则不缓存
        """
        self.cache_dir = cache_dir
        self.ico_size = (256, 256)  # ICO 文件尺寸
        self.twemoji_base = "https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.0.3/assets/72x72/"

        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _emoji_to_twicode(self, emoji):
        """
        将 Emoji 转换为 Twemoji 文件名

        Args:
            emoji: Emoji 字符

        Returns:
            Twemoji 文件名（不含扩展名）
        """
        # 将 emoji 转换为 Unicode 码点（十六进制）
        codepoints = [f"{ord(c):x}" for c in emoji]
        return "-".join(codepoints)

    def _download_emoji_image(self, emoji):
        """
        从 Twemoji CDN 下载 Emoji 图片

        Args:
            emoji: Emoji 字符

        Returns:
            PIL.Image 对象
        """
        twemoji_filename = self._emoji_to_twicode(emoji)
        url = f"{self.twemoji_base}{twemoji_filename}.png"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # 从下载的数据创建图片
            from io import BytesIO
            img = Image.open(BytesIO(response.content))

            # 转换为 RGBA 并调整大小
            img = img.convert("RGBA").resize(self.ico_size, Image.Resampling.LANCZOS)

            return img
        except Exception as e:
            print(f"下载 Emoji 失败: {e}")
            raise Exception(f"无法下载 Emoji 图片: {e}")

    def convert(self, emoji, folder_path):
        """
        将 Emoji 转换为 .ico 文件

        Args:
            emoji: Emoji 字符，如 "📁"
            folder_path: 目标文件夹路径

        Returns:
            ico_path: 生成的 .ico 文件绝对路径
        """
        # Input validation
        if not emoji or not isinstance(emoji, str) or not emoji.strip():
            raise ValueError("Invalid emoji input: must be a non-empty string")

        # 生成文件名（使用 emoji 的 Unicode 码点或哈希值）
        if len(emoji) == 1:
            # 单字符 emoji，直接用 Unicode 码点
            emoji_code = hex(ord(emoji))[2:]
        else:
            # 组合 emoji（如带皮肤色调、flag 等），用 MD5 哈希
            emoji_hash = hashlib.md5(emoji.encode('utf-8')).hexdigest()[:8]
            emoji_code = f"combo_{emoji_hash}"

        ico_filename = f".folder_{emoji_code}.ico"

        # 决定保存位置
        if self.cache_dir:
            # 缓存模式：保存到统一缓存目录
            ico_path = os.path.join(self.cache_dir, ico_filename)
        else:
            # 本地模式：保存到目标文件夹内（隐藏文件）
            ico_path = os.path.join(folder_path, ico_filename)

        # 如果已存在，直接返回
        if os.path.exists(ico_path):
            return ico_path

        # 从 CDN 下载 Emoji 并转换为 ICO
        img = self._download_emoji_image(emoji)

        # 保存为 ICO 格式
        img.save(ico_path, format='ICO', sizes=[(256, 256)])

        return ico_path
