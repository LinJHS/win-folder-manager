# -*- coding: utf-8 -*-
"""
AI 命名服务 - 兼容 OpenAI API 格式
支持官方 OpenAI API 及第三方兼容接口（如 DeepSeek、OneAPI 等）
"""

import requests
import json
import re


class AINamingService:
    """AI 命名服务"""

    def __init__(self, ai_config):
        """
        初始化 AI 服务

        Args:
            ai_config: 包含 api_base, api_key, model 的字典
        """
        self.api_base = ai_config.get('api_base', 'https://api.openai.com/v1')
        self.api_key = ai_config.get('api_key', '')
        self.model = ai_config.get('model', 'gpt-3.5-turbo')

    def _build_prompt(self, folder_name):
        """构造 AI Prompt"""
        return f"""你是一个文件夹命名专家。请根据以下文件夹名称，生成一个中文别名和一个合适的 Emoji 图标。

文件夹名称: {folder_name}

请严格按以下 JSON 格式返回（不要有任何其他文字）：
{{
    "alias": "中文名称（2-6个字）",
    "infotip": "简短备注（10-20字，可选填）",
    "emoji": "一个相关的Emoji图标"
}}

命名规则：
1. alias: 简洁易懂的中文名称，例如：
   - "MyProject" → "我的项目"
   - "Downloads" → "下载目录"
   - "230214_Meeting" → "230214_会议记录"

2. infotip: 可选，描述文件夹用途

3. emoji: 选择最相关的 Emoji，例如：
   - 项目文件夹: 📁
   - 代码: 💻
   - 文档: 📄
   - 图片: 🖼️
   - 音乐: 🎵
   - 下载: ⬇️
   - 工作: 💼
   - 学习: 📚

只返回 JSON，不要任何解释。"""

    def generate(self, folder_name):
        """
        调用 AI API 生成命名

        Args:
            folder_name: 文件夹名称

        Returns:
            包含 status, alias, infotip, emoji 的字典
        """
        if not self.api_key:
            raise Exception("API Key 未配置")

        url = f"{self.api_base.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": self._build_prompt(folder_name)}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()

            if 'choices' not in result or len(result['choices']) == 0:
                raise Exception("API 返回了空的选择列表 (choices is empty)")

            content = result['choices'][0]['message']['content'].strip()
            
            if not content:
                raise Exception("AI 返回的内容为空 (content is empty)")

            # 更加强健的 JSON 提取逻辑
            json_str = content
            
            # 1. 优先尝试提取 markdown 代码块中的 JSON
            code_block_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", content, re.IGNORECASE)
            if code_block_match:
                json_str = code_block_match.group(1)
            else:
                # 2. 如果没有代码块，尝试提取最外层的 {} 包裹的内容
                brace_match = re.search(r"\{[\s\S]*\}", content)
                if brace_match:
                    json_str = brace_match.group(0)
            
            # 3. 尝试解析
            try:
                ai_result = json.loads(json_str)
            except json.JSONDecodeError:
                # 4. 容错处理：尝试清理常见的 JSON 格式错误（如尾部逗号）
                try:
                    # 去除对象末尾多余的逗号
                    fixed_json = re.sub(r",\s*\}", "}", json_str)
                    fixed_json = re.sub(r",\s*\]", "]", fixed_json)
                    ai_result = json.loads(fixed_json)
                except Exception:
                    # 记录原始返回内容以便调试
                    print(f"JSON Parse Error. Raw content: {content}")
                    raise Exception("AI 返回的不是有效 JSON，请检查日志或重试")

            return {
                "status": "success",
                "alias": ai_result.get('alias', ''),
                "infotip": ai_result.get('infotip', ''),
                "emoji": ai_result.get('emoji', '📁')
            }

        except requests.exceptions.RequestException as e:
            raise Exception(f"API 请求失败: {str(e)}")
        except KeyError as e:
            raise Exception(f"AI 响应格式异常: {str(e)}")
