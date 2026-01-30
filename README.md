# TXT Splitter / TXT 文档拆分工具

<div align="center">

**一款专为小说作家打造的文档拆分工具 | A Document Splitter Designed for Novelists**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.6+-green.svg)](https://www.python.org/downloads/)

[English](#english) | [中文](#chinese)

</div>

---

## Chinese

### 📖 简介
**TXT文档拆分工具** 是一款轻量级、界面现代的桌面应用程序，专为处理长文本（尤其是小说和网络小说）而设计。它能够智能识别章节标题，将数百万字的长篇小说拆分成独立的小文件或合并导出。

### ✨ 为什么作家需要它？
随着 AI（如 ChatGPT, Claude, 文心一言等）在创作辅助中的普及，作家们经常需要将庞大的作品上传给 AI 进行剧情梳理、大纲生成或风格润色。

然而，大多数 AI 模型都有上下文长度限制，无法一次性“吃下”几百万字的文档。本工具完美解决了这一痛点：
*   **📚 智能拆分：** 自动识别“第XX章”标题，将长书按章节切分。
*   **🤖 AI 友好：** 拆分后的文件方便作家分批上传给 AI，快速生成**全书剧情大纲**或**分章摘要**。
*   **⚙️ 灵活控制：** 支持按章节拆分，或按字符数拆分（例如每 10 万字一个文件）。

### ✨ 主要功能
*   🧠 **智能章节识别**：支持正则匹配，自动识别多种格式的章节标题（如“第一章”、“Chapter 1”等）。
*   📂 **灵活的导出选项**：
    *   **按章节导出**：每章生成一个独立文件。
    *   **按大小导出**：根据字符数自动切割，适合上传有字数限制的平台。
    *   **合并导出**：将选中的多个章节合并为一个文件（例如 `小说名-1~10.txt`）。
*   ✏️ **自定义文件名**：导出前支持修改默认文件名，方便管理。
*   🎨 **现代 UI**：采用苹果风格设计，支持 4K/高 DPI 屏幕，视觉体验舒适。
*   💾 **多格式支持**：导出为纯文本 (TXT) 或 Markdown (MD) 格式。

### 🚀 快速开始

#### 环境要求
*   Python 3.6 或更高版本

#### 安装与运行

**方法一：直接运行源码**
```bash
# 1. 克隆或下载仓库
git clone https://github.com/zoeyzhang233666/txt-splitter.git
cd txt-splitter

# 2. 运行程序
python txt_splitter.py
```

**方法二：使用 PyInstaller 打包（推荐）**
如果您不想安装 Python 环境，可以将其打包为 `.exe` 文件：

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包
pyinstaller -F -n "TXT拆分工具" -i icon.ico txt_splitter.py
```
*注：请在代码目录下准备好 `icon.ico` 图标文件，或者去掉 `-i` 参数。*

### 📸 使用场景示例
> **场景：** 您刚刚完成了一本 200 万字的网络小说，想用 AI 帮您总结全书的故事线和人物关系。

1.  使用本工具打开 TXT 文件，点击“识别章节”。
2.  选择“导出全部”，并选择“合并导出到单个文件”（或者按大小拆分为 10 万字一份）。
3.  将生成的文件依次喂给 AI：“这是小说的前 10 章内容，请帮我总结这一阶段的剧情冲突...”

### 🤝 贡献
欢迎提交 Issue 和 Pull Request！

### 📄 许可证
MIT License

---

## English

### 📖 About
**TXT Splitter** is a lightweight, modern desktop application designed specifically for handling long texts, especially novels and web fiction. It intelligently identifies chapter titles and splits multi-million-word novels into independent files or merges them for export.

### ✨ Why Novelists Need It?
With the rise of AI (like ChatGPT, Claude, etc.) in creative assistance, writers often need to upload massive works to AI for plot outlining, summarization, or style polishing.

However, most AI models have context window limits and cannot process millions of words at once. This tool solves that pain point perfectly:
*   **📚 Smart Splitting:** Automatically recognizes chapter titles (e.g., "Chapter 1") to split long books.
*   **🤖 AI Friendly:** Split files allow writers to batch-upload content to AI to generate **full story outlines** or **chapter summaries** efficiently.
*   **⚙️ Flexible Control:** Support splitting by chapter or by character count (e.g., one file per 100k words).

### ✨ Features
*   🧠 **Smart Chapter Detection:** Uses regex patterns to automatically identify various chapter formats (e.g., "第一章", "Chapter 1", "Ep. 1").
*   📂 **Flexible Export Options:**
    *   **By Chapter:** Export each chapter as a separate file.
    *   **By Size:** Split files based on character limit (useful for platforms with upload limits).
    *   **Merge Export:** Combine selected chapters into a single file (e.g., `NovelName-1~10.txt`).
*   ✏️ **Custom Filenames:** Supports modifying the default filename before exporting for better organization.
*   🎨 **Modern UI:** Apple-style design with 4K/High DPI screen support for a comfortable visual experience.
*   💾 **Multi-format:** Export as Plain Text (TXT) or Markdown (MD).

### 🚀 Quick Start

#### Requirements
*   Python 3.6+

#### Installation & Run

**Method 1: Run Source Code**
```bash
# 1. Clone or download the repo
git clone https://github.com/yourusername/txt-splitter.git
cd txt-splitter

# 2. Run the app
python txt_splitter.py
```

**Method 2: Package with PyInstaller (Recommended)**
If you want a standalone `.exe` file without installing Python:

```bash
# Install PyInstaller
pip install pyinstaller

# Package
pyinstaller -F -n "TXT Splitter" -i icon.ico txt_splitter.py
```
*Note: Make sure you have an `icon.ico` file in the directory, or remove the `-i` parameter.*

### 📸 Use Case Scenario
> **Scenario:** You have just finished a 2-million-word web novel and want to use AI to summarize the story arc and character relationships.

1.  Open the TXT file with this tool and click "Detect Chapters".
2.  Select "Export All" and choose "Merge to single file" (or split by size into 100k chunks).
3.  Feed the generated files to the AI sequentially: "Here are the first 10 chapters. Please summarize the plot conflicts in this section..."

### 🤝 Contributing
Issues and Pull Requests are welcome!

### 📄 License
MIT License
