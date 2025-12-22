import os
import json
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

# 初始化逻辑类
folder_logic = FolderManager(CONFIG_FILE)


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"root_path": "", "icons": []}
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


@app.route('/')
def index():
    return render_template('index.html')


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
