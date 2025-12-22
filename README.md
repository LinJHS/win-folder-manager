<div align="center">

<img src="imgs/Logo-Text.jpg" width="100%" alt="Win Folder Manager">

<br>

[![PyPI version](https://img.shields.io/pypi/v/win-folder-manager.svg?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/win-folder-manager/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/win-folder-manager.svg?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/win-folder-manager/)
[![Docker Pulls](https://img.shields.io/docker/pulls/linjhs/win-folder-manager.svg?style=flat-square&logo=docker&logoColor=white)](https://hub.docker.com/r/linjhs/win-folder-manager)
[![Build Status](https://github.com/LinJHS/win-folder-manager/actions/workflows/publish.yml/badge.svg)](https://github.com/LinJHS/win-folder-manager/actions)
[![Python Versions](https://img.shields.io/pypi/pyversions/win-folder-manager.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/win-folder-manager/)
[![License](https://img.shields.io/github/license/LinJHS/win-folder-manager.svg?style=flat-square)](https://github.com/LinJHS/win-folder-manager/blob/main/LICENSE)

**一个轻量级的、基于 Web 的 Windows 文件夹自定义工具。**

[English Version](README_EN.md) | [Wiki](https://github.com/LinJHS/win-folder-manager/wiki) | [功能特性](#-功能特性) • [安装](#-安装) • [使用](#-使用) • [Docker](#-docker-支持) • [开发](#-开发)

</div>

---

**Win Folder Manager** 允许您通过简洁的 Web 界面轻松自定义 Windows 文件夹。无需手动编辑隐藏的系统文件，即可设置自定义图标、别名（本地化名称）和提示信息。

## ✨ 功能特性

- 🖼️ **自定义图标**：轻松设置文件夹图标（支持绝对路径和相对路径）。
- 🏷️ **文件夹别名**：在资源管理器中直观地重命名文件夹显示，而不改变实际目录名称。
- ℹ️ **提示信息**：为文件夹添加自定义悬停文本描述 (InfoTip)。
- 🔄 **批量操作**：批量将绝对图标路径转换为相对路径，便于移动设备使用。
- 📂 **快速操作**：直接从 UI 在资源管理器或 CMD 中打开文件夹。
- 🚀 **Web 界面**：基于 Flask 的简单 UI，通过浏览器即可访问。
- 💾 **持久化配置**：配置文件自动保存到 `%APPDATA%`，更新不丢失。

## 📸 界面预览

> **核心功能展示**：物理路径保持不变（英文），但在资源管理器中显示为中文别名。
> 
> <img src="imgs/00-concept.png" width="100%">

| 管理主页 | 属性编辑 |
| :---: | :---: |
| <img src="imgs/02-dashboard.png" width="100%"> | <img src="imgs/03-edit-attributes.png" width="100%"> |
| **配置页面** | **资源管理器效果** |
| <img src="imgs/01-configuration.png" width="100%"> | <img src="imgs/04-explorer-preview.png" width="100%"> |

## 📦 安装

### 通过 PyPI 安装 (推荐)

```bash
pip install win-folder-manager
```

### 通过源码安装

```bash
git clone https://github.com/LinJHS/win-folder-manager.git
cd win-folder-manager
pip install .
```

> **注意**：如果您在 Linux 或 Docker 环境下开发，请使用 `requirements-docker.txt` 安装依赖，以避免 `pywin32` 安装失败：
> ```bash
> pip install -r requirements-docker.txt
> ```

## 🚀 使用

安装完成后，只需运行：

```bash
win-folder-manager
```

或者直接使用 python 模块运行：

```bash
python -m manager
```

程序将启动一个本地 Web 服务器（默认端口：`6800`）并自动打开您的默认浏览器。

### 命令行选项

您可以使用以下参数自定义启动行为：

- `-p`, `--port`: 指定服务器端口 (默认: 6800)
- `--host`: 指定监听地址 (默认: 127.0.0.1)
- `--no-browser`: 启动时不自动打开浏览器
- `--debug`: 开启 Flask 调试模式

示例：

```bash
# 在端口 9000 启动
win-folder-manager -p 9000

# 允许局域网访问
win-folder-manager --host 0.0.0.0

# 仅启动服务器，不打开浏览器
win-folder-manager --no-browser
```

### 配置

配置文件存储在：
`%APPDATA%\win-folder-manager\config.json`

您可以在 Web 界面中直接配置需要扫描管理的根目录路径。

## 🐳 Docker 支持

您可以使用 Docker 运行 Win Folder Manager。

```bash
docker run -d \
  -p 6800:6800 \
  -v /path/to/your/folders:/data \
  -v win-folder-manager-config:/root/.config/win-folder-manager \
  linjhs/win-folder-manager
```

> **注意**：本应用依赖 Windows 特有的命令 (`attrib`) 来设置文件夹属性（系统/隐藏/只读），这是 `desktop.ini` 自定义生效的必要条件。在 Linux 容器中运行可能会限制部分功能，除非用于特定环境或仅作查看用途。

## 🛠️ 开发

1. 克隆仓库
   ```bash
   git clone https://github.com/LinJHS/win-folder-manager.git
   ```
2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```
3. 本地运行
   ```bash
   python -m manager
   ```

## 📄 许可证

本项目采用 GNU General Public License v3.0 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。
