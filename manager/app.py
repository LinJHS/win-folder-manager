import os
import json
import time
import webbrowser
from threading import Timer
from flask import Flask, render_template, jsonify, request
from .logic import FolderManager

import sys

# Use APPDATA for persistent config storage
def get_config_dir():
    if os.name == 'nt':
        # Windows: %APPDATA%\win-folder-manager
        return os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'win-folder-manager')
    else:
        # Linux/Docker: ~/.config/win-folder-manager
        # Respect XDG_CONFIG_HOME
        xdg_config = os.environ.get('XDG_CONFIG_HOME')
        if xdg_config:
            return os.path.join(xdg_config, 'win-folder-manager')
        return os.path.join(os.path.expanduser('~'), '.config', 'win-folder-manager')

APPDATA_DIR = get_config_dir()
if not os.path.exists(APPDATA_DIR):
    os.makedirs(APPDATA_DIR)

CONFIG_FILE = os.path.join(APPDATA_DIR, 'config.json')

# Define paths for templates and static files
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    BASE_DIR = os.path.join(sys._MEIPASS, 'manager')
else:
    # Running in normal Python environment
    BASE_DIR = os.path.dirname(__file__)

TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)

# Try to import version
try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0+unknown"

# 初始化逻辑类
folder_logic = FolderManager(CONFIG_FILE)


def load_config():
    default_ai_config = {
        "enabled": False,
        "active_provider": "DeepSeek",
        "providers": [
            {
                "name": "SiliconFlow",
                "api_base": "https://api.siliconflow.cn/v1",
                "api_key": "",
                "model": "deepseek-ai/DeepSeek-V3.2",
                "models": ["deepseek-ai/DeepSeek-V3.2", "google/gemma-3-9b-it", "qwen/qwen3-7b-chat"]
            },
            {
                "name": "DeepSeek",
                "api_base": "https://api.deepseek.com",
                "api_key": "",
                "model": "deepseek-chat",
                "models": ["deepseek-chat"]
            },
            {
                "name": "Zhipu",
                "api_base": "https://open.bigmodel.cn/api/paas/v4",
                "api_key": "",
                "model": "glm-4.7-flash",
                "models": ["glm-4.7-flash", "glm-4v-flash"]
            },
            {
                "name": "OpenAI",
                "api_base": "https://api.openai.com/v1",
                "api_key": "",
                "model": "gpt-5-nano",
                "models": ["gpt-5-nano", "gpt-5-mini", "gpt-4o-mini"]
            },
            {
                "name": "Anthropic",
                "api_base": "https://api.anthropic.com/v1",
                "api_key": "",
                "model": "claude-4.5-haiku",
                "models": ["claude-4.5-haiku", "claude-3.5-haiku"]
            },
            {
                "name": "Google",
                "api_base": "https://generativelanguage.googleapis.com/v1beta",
                "api_key": "",
                "model": "gemini-3-flash",
                "models": ["gemini-3-flash", "gemini-2.5-flash-lite"]
            },
            {
                "name": "Groq",
                "api_base": "https://api.groq.com/openai/v1",
                "api_key": "",
                "model": "llama-4-maverick",
                "models": ["llama-4-maverick", "llama-3.1-8b-instant"]
            },
            {
                "name": "OpenRouter",
                "api_base": "https://openrouter.ai/api/v1",
                "api_key": "",
                "model": "openai/gpt-4o-mini",
                "models": ["openai/gpt-5-nano", "openai/gpt-5-mini", "openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet", "google/gemini-flash-1.5", "deepseek/deepseek-chat"]
            },
            {
                "name": "Alibaba-Qwen",
                "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "api_key": "",
                "model": "qwen3-8b-instruct",
                "models": ["qwen3-8b-instruct", "qwen-turbo-latest", "qwen3-omni-flash"]
            }
        ]
    }

    if not os.path.exists(CONFIG_FILE):
        return {
            "root_path": "",
            "icons": [],
            "ai_config": default_ai_config
        }

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception:
        return {
            "root_path": "",
            "icons": [],
            "ai_config": default_ai_config
        }

    # 确保 ai_config 字段存在
    if 'ai_config' not in config:
        config['ai_config'] = default_ai_config
    else:
        # 检查 ai_config 内部字段，如果缺失则使用默认值填充
        ai_config = config['ai_config']
        if 'providers' not in ai_config or not ai_config['providers']:
            ai_config['providers'] = default_ai_config['providers']
        if 'active_provider' not in ai_config:
            ai_config['active_provider'] = default_ai_config['active_provider']

    # Emoji 配置初始化
    if 'emoji_save_mode' not in config:
        # 模式: 'global' (全局目录) 或 'relative' (根目录下相对目录)
        config['emoji_save_mode'] = 'global'

    if 'emoji_global_dir' not in config:
        # 使用默认
        config['emoji_global_dir'] = os.path.join(APPDATA_DIR, 'emoji_cache')

    if 'emoji_relative_name' not in config:
        # 相对模式下的文件夹名称
        config['emoji_relative_name'] = '.emoji_cache'

    return config


def save_config(data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


@app.route('/')
def index():
    return render_template('index.html', version=__version__)


@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    if request.method == 'POST':
        new_config = request.json
        save_config(new_config)
        return jsonify({"status": "success"})
    return jsonify(load_config())


@app.route('/api/select_folder', methods=['POST'])
def select_folder_dialog():
    if os.name != 'nt':
        return jsonify({"status": "error", "msg": "Folder selection is only supported on Windows."})

    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        return jsonify({"status": "error", "msg": "Tkinter module not found. Please ensure Python is installed with tcl/tk support."})

    try:
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw() # Hide the main window

        # Set custom icon if exists
        icon_path = os.path.join(STATIC_FOLDER, 'favicon.ico')
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)

        root.attributes('-topmost', True) # Make it appear on top
        
        # Open directory picker
        folder_selected = filedialog.askdirectory()
        
        root.destroy()
        
        if folder_selected:
            # Normalize path separator for Windows
            path = os.path.normpath(folder_selected)
            return jsonify({"status": "success", "path": path})
        else:
            return jsonify({"status": "cancel"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})


@app.route('/api/select_file', methods=['POST'])
def select_file_dialog():
    if os.name != 'nt':
        return jsonify({"status": "error", "msg": "File selection is only supported on Windows."})

    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        return jsonify({"status": "error", "msg": "Tkinter module not found."})

    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        file_path = filedialog.askopenfilename(
            title="Select Icon or Image",
            filetypes=[("Image files", "*.ico;*.png;*.jpg;*.jpeg;*.bmp;*.webp"), ("All files", "*.*")]
        )
        
        root.destroy()
        
        if file_path:
            path = os.path.normpath(file_path)
            return jsonify({"status": "success", "path": path})
        else:
            return jsonify({"status": "cancel"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})


@app.route('/api/convert_to_ico', methods=['POST'])
def convert_image_to_ico():
    from .icon_converter import IconConverter

    data = request.json
    source_path = data.get('source_path')
    
    if not source_path or not os.path.exists(source_path):
        return jsonify({"status": "error", "msg": "File not found"}), 400
        
    try:
        config = load_config()
        
        # Determine cache dir based on save mode
        # Prioritize parameters from request (UI state), fallback to saved config
        mode = data.get('emoji_save_mode', config.get('emoji_save_mode', 'global'))
        root = data.get('root_path', config.get('root_path', ''))
        relative_name = data.get('emoji_relative_name', config.get('emoji_relative_name', '.emoji_cache'))
        global_dir = data.get('emoji_global_dir', config.get('emoji_global_dir'))

        cache_dir = None

        if mode == 'relative':
            if root:
                cache_dir = os.path.join(root, relative_name)
        
        # Fallback to global if relative failed or mode is global
        if not cache_dir:
            cache_dir = global_dir
            
        # Final fallback if global dir is missing in config
        if not cache_dir:
             cache_dir = os.path.join(get_config_dir(), 'icons')
             
        converter = IconConverter(cache_dir)
        ico_path = converter.convert_from_file(source_path)
            
        return jsonify({"status": "success", "ico_path": ico_path})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500


@app.route('/api/folders')
def get_folders():
    config = load_config()
    root = config.get('root_path', '')
    if not root:
        return jsonify([])
    folders = folder_logic.scan_folders(root)
    return jsonify(folders)


@app.route('/api/update', methods=['POST'])
def update_folder():
    data = request.json
    path = data.get('path')
    alias = data.get('alias')
    icon_path = data.get('icon_path')
    infotip = data.get('infotip')
    use_relative = data.get('use_relative', False)

    if not path:
        return jsonify({"status": "error", "msg": "No path provided"}), 400

    try:
        folder_logic.update_folder(
            path, alias, icon_path, infotip, use_relative)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500


@app.route('/api/open', methods=['POST'])
def open_path():
    data = request.json
    path = data.get('path')
    mode = data.get('mode', 'explorer')  # explorer or cmd

    if not path or not os.path.exists(path):
        return jsonify({"status": "error", "msg": "Path not found"})

    if mode == 'cmd':
        os.system(f'start cmd /k "cd /d {path}"')
    else:
        os.startfile(path)

    return jsonify({"status": "success"})


@app.route('/api/batch_relative', methods=['POST'])
def batch_relative():
    """将所有文件夹的配置尝试转换为相对路径"""
    config = load_config()
    root = config.get('root_path', '')
    folders = folder_logic.scan_folders(root)

    count = 0
    for folder in folders:
        if folder['has_ini']:
            folder_logic.update_folder(
                folder['path'],
                folder['alias'],
                folder['icon_path'],
                folder['infotip'],
                use_relative=True
            )
            count += 1
    return jsonify({"status": "success", "count": count})


@app.route('/api/ai_generate', methods=['POST'])
def ai_generate():
    """AI 生成别名和 Emoji"""
    from .ai_service import AINamingService

    data = request.json
    folder_name = data.get('folder_name', '')
    
    # 从服务端加载配置，不再依赖前端传来的敏感信息
    config = load_config()
    ai_config = config.get('ai_config', {})
    
    if not ai_config.get('enabled'):
        return jsonify({"status": "error", "msg": "AI 功能未启用"}), 400

    # 获取当前激活的提供商配置
    active_name = ai_config.get('active_provider')
    provider_config = None
    for p in ai_config.get('providers', []):
        if p['name'] == active_name:
            provider_config = p
            break
            
    if not provider_config:
        return jsonify({"status": "error", "msg": "未找到有效的 AI 提供商配置"}), 400

    if not folder_name:
        return jsonify({"status": "error", "msg": "文件夹名称不能为空"}), 400

    try:
        service = AINamingService(provider_config)
        result = service.generate(folder_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500


@app.route('/api/emoji_to_ico', methods=['POST'])
def emoji_to_ico():
    """将 Emoji 转换为 .ico 文件"""
    from .icon_converter import IconConverter

    data = request.json
    emoji = data.get('emoji', '')
    folder_path = data.get('folder_path', '')

    if not emoji or not folder_path:
        return jsonify({"status": "error", "msg": "参数不完整"}), 400

    try:
        config = load_config()
        
        # 确定缓存目录
        mode = config.get('emoji_save_mode', 'global')
        if mode == 'relative':
            # 相对模式：需要知道根目录
            root = config.get('root_path', '')
            if root:
                cache_dir = os.path.join(root, config.get('emoji_relative_name', '.emoji_cache'))
            else:
                # 如果没有根目录（理论上不应发生），回退到全局或 None
                cache_dir = config.get('emoji_global_dir')
        else:
            # 全局模式
            cache_dir = config.get('emoji_global_dir')

        converter = IconConverter(cache_dir)
        ico_path = converter.convert_emoji(emoji, folder_path)

        return jsonify({"status": "success", "ico_path": ico_path})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500


@app.route('/api/batch_ai_generate', methods=['POST'])
def batch_ai_generate():
    """批量 AI 生成文件夹别名"""
    from .ai_service import AINamingService
    from .icon_converter import IconConverter

    data = request.json
    
    # 速率限制配置
    batch_size = data.get('batch_size', 5)      # 默认每批处理 5 个
    # delay = data.get('delay', 2.0)            # 不再使用固定延迟

    try:
        config = load_config()
        root = config.get('root_path', '')
        
        # 确定缓存目录
        mode = config.get('emoji_save_mode', 'global')
        if mode == 'relative':
            if root:
                cache_dir = os.path.join(root, config.get('emoji_relative_name', '.emoji_cache'))
            else:
                cache_dir = config.get('emoji_global_dir')
        else:
            cache_dir = config.get('emoji_global_dir')
            
        ai_config = config.get('ai_config', {})

        if not root:
            return jsonify({"status": "error", "msg": "根目录未配置"}), 400
            
        if not ai_config.get('enabled'):
            return jsonify({"status": "error", "msg": "AI 功能未启用"}), 400

        # 获取当前激活的提供商配置
        active_name = ai_config.get('active_provider')
        provider_config = None
        for p in ai_config.get('providers', []):
            if p['name'] == active_name:
                provider_config = p
                break
        
        if not provider_config:
            return jsonify({"status": "error", "msg": "未找到有效的 AI 提供商配置"}), 400

        folders = folder_logic.scan_folders(root)
        service = AINamingService(provider_config)
        converter = IconConverter(cache_dir)

        count = 0
        errors = []
        
        # 筛选出需要处理的文件夹
        targets = [f for f in folders if not f.get('alias')]
        
        # 应用批次限制
        targets = targets[:batch_size]

        for folder in targets:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    result = service.generate(folder['name'])
                    if result['status'] == 'success':
                        ico_path = converter.convert_emoji(result['emoji'], folder['path'])
                        folder_logic.update_folder(
                            folder['path'],
                            result['alias'],
                            ico_path,
                            result.get('infotip', ''),
                            use_relative=True
                        )
                        count += 1
                    break # 成功则跳出重试循环
                except Exception as e:
                    err_msg = str(e).lower()
                    # 检查是否为速率限制错误 (429, rate limit, too many requests)
                    is_rate_limit = "429" in err_msg or "rate limit" in err_msg or "too many requests" in err_msg
                    
                    if is_rate_limit and attempt < max_retries - 1:
                        # 指数退避: 1s, 2s, 4s...
                        sleep_time = 2 ** attempt
                        time.sleep(sleep_time)
                        continue
                    
                    # 如果是最后一次尝试，或者不是速率限制错误，则记录错误
                    if attempt == max_retries - 1:
                        errors.append(f"{folder['name']}: {str(e)}")

        return jsonify({
            "status": "success",
            "count": count,
            "errors": errors,
            "has_more": len([f for f in folders if not f.get('alias')]) > count
        })
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500


def open_browser(port):
    webbrowser.open_new(f"http://127.0.0.1:{port}")


def start_server(host='127.0.0.1', port=6800, debug=False, open_browser_on_start=True):
    if open_browser_on_start:
        Timer(1, lambda: open_browser(port)).start()
    
    try:
        app.run(host=host, port=port, debug=debug)
    except OSError as e:
        import sys
        # Handle "Address already in use" error
        if e.errno == 98 or e.errno == 10048:
            print(f"\nError: Port {port} is already in use.")
            print("Please try using a different port with the --port argument.")
            print(f"Example: win-folder-manager --port {port + 1}\n")
            sys.exit(1)
        raise


def main():
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Win Folder Manager")
    parser.add_argument("-p", "--port", type=int, default=6800, help="Port to run the server on (default: 6800)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser on start")
    
    args = parser.parse_args()
    
    if not (1 <= args.port <= 65535):
        print("\nError: Port must be between 1 and 65535.\n")
        sys.exit(1)
    
    start_server(host=args.host, port=args.port, debug=args.debug, open_browser_on_start=not args.no_browser)


# Alias for backward compatibility or direct import usage
run = start_server


if __name__ == '__main__':
    main()
