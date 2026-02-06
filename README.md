# Splitter / 文档拆分工具

<div align="center">

**一款专为小说作家与 AI 创作者打造的文档处理利器**

**A Professional Document Splitter for Novelists & AI Creators**

[English](https://www.google.com/search?q=%23english) | [中文](https://www.google.com/search?q=%23chinese)

</div>

---

<a name="chinese"></a>

## 🇨🇳 中文说明

### 📖 简介

**文档拆分工具** 是一款轻量级、界面现代的桌面应用程序，专为处理长文本（尤其是小说和网络小说）而设计。它能够智能识别章节标题，将数百万字的长篇小说拆分成独立的小文件或合并导出。

### ✨ 为什么作家需要它？

随着 AI（如 ChatGPT, Claude, DeepSeekl等）在创作辅助中的普及，作家们经常需要将庞大的作品上传给 AI 进行剧情梳理、大纲生成或风格润色。

然而，大多数 AI 模型都有上下文长度限制，无法一次性“吃下”几百万字的文档。本工具完美解决了这一痛点：

- **📚 智能拆分：** 自动识别“第XX章”、"Chapter" 或数字序号标题，将长书按章节切分。
    
- **🤖 AI 友好：** 拆分后的文件方便作家分批上传给 AI，快速生成**全书剧情大纲**或**分章摘要**。
    
- **📂 灵活的导出选项**：
    
    - **按章节导出**：每章生成一个独立文件。
        
    - **按大小导出**：根据 MB 阈值自动切割，适合上传有字数限制的平台。
        
    - **合并导出**：将选中的多个章节合并为一个文件（例如 `小说名-合并导出.txt`）。
        
    - **批量等量合并**：每 N 章节合并导出，文件名会自动生成如 `1~10章` 的区间标识。
        
- **🏷️ 文件命名方式**：支持自定义“原文件名、序号、章节名”的组合。系统会自动过滤文件名中的非法字符以确保兼容性。
    
- **📚 电子书多格式支持**：除了 **纯文本 (TXT)**，还支持直接读取 **Epub** 和 **Mobi** 格式，支持导出为 **纯文本 (TXT)** 或 **Markdown (MD)** 格式。
    
    - _注：导出为 Markdown 时，程序会自动处理标题冗余并添加 # 层级。_
        
- **🛠️ 编码自动识别**：深度适配中文环境，自动识别 UTF-8, GB18030, GBK 等文本编码，拒绝乱码。
    

### 🚀 快速开始

#### 环境要求

- Windows 10/11 系统
    
- 无需安装 Python 环境（使用 Release 版本）
    

#### 安装与运行

**方法一：下载运行（推荐）**

1. 在本仓库的 [Releases](https://www.google.com/search?q=../../releases) 页面下载最新的 `文档拆分工具.exe` 文件。
    
2. 双击运行即可使用，无需安装。
    

**方法二：运行源码（开发者）**

如果您想修改源代码或使用 Python 运行：

Bash

```
# 1. 克隆或下载仓库
git clone https://github.com/yourusername/txt-splitter.git
cd txt-splitter

# 2. 安装依赖
pip install ebooklib beautifulsoup4 mobi

# 3. 运行程序
python txt_splitter.py
```

### 📸 使用场景示例

> **场景：** 您刚刚完成了一本 200 万字的网络小说，想用 AI 帮您总结全书的故事线和人物关系。

1. 使用本工具打开小说文件，点击“识别章节”。
    
2. 勾选您想分析的范围。
    
3. 选择“执行批量合并”，设置每 10 章合并为一个文件。
    
4. 将生成的 `书名_1~10章.txt` 依次喂给 AI：“这是小说的前 10 章内容，请按照我的拆书提示词总结这一阶段的网格化剧情细纲…….”
    

---

<a name="english"></a>

## 🇺🇸 English Description

### 📖 Introduction

**Splitter** is a lightweight, modern desktop application designed for processing large-scale text, particularly web novels. It intelligently detects chapter headings and can split multi-million-word manuscripts into individual files or merge them into structured segments.

### ✨ Why Creators Need It?

With the rise of AI (ChatGPT, Claude, etc.) in creative writing, authors often need to upload massive works for plot analysis, outline generation, or style polishing.

However, most AI models have context window limits. This tool solves this pain point:

- **📚 Smart Splitting:** Automatically identifies "Chapter X", "第XX章", or numeric patterns to split long books.
    
- **🤖 AI-Friendly:** Processed files are easy to upload in batches, helping you generate **full-book outlines** or **chapter summaries** quickly.
    
- **📂 Flexible Export Options**:
    
    - **Individual Chapters**: One file per chapter.
        
    - **Split by Size**: Automatically cut files based on MB size to fit platform limits.
        
    - **Single Merge**: Merge all selected chapters into one file.
        
    - **Batch Merge**: Merge every N chapters into one file with auto-labeled ranges (e.g., `1~10_Chapters`).
        
- **🏷️ Customizable Naming**: Combine [Original Filename], [Index], and [Chapter Title]. Illegal characters are automatically cleaned for OS compatibility.
    
- **📚 Multi-format Support**: Supports **TXT**, **Epub**, and **Mobi** for import. Supports **TXT** and **Markdown (MD)** for export.
    
    - _Note: The Markdown exporter optimizes headers and removes redundant titles._
        
- **🛠️ Encoding Detection**: Automatically recognizes UTF-8, GB18030, and GBK to prevent garbled text.
    

### 🚀 Quick Start

#### Requirements

- Windows 10/11
    
- Python 3.8+ (for running from source)
    

#### Installation & Usage

**Method 1: Download Executable (Recommended)**

1. Download the latest `txt_splitter.exe` from the [Releases](https://www.google.com/search?q=../../releases) page.
    
2. Double-click to run.
    

**Method 2: Run from Source**

Bash

```
git clone https://github.com/yourusername/txt-splitter.git
cd txt-splitter
pip install ebooklib beautifulsoup4 mobi
python txt_splitter.py
```

---

### 🤝 贡献 / Contribution

欢迎提交 Issue 和 Pull Request！ / Feel free to submit Issues and Pull Requests!

### 📄 许可证 / License

MIT License
