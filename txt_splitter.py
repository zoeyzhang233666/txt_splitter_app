#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TXT文档拆分工具
支持识别章节、选择导出、批量导出、按章节或大小分割
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import re
import os
import sys
import json
from pathlib import Path
from typing import List, Tuple, Optional

# --- DPI 设置开始 (解决 4K 屏模糊) ---
try:
    from ctypes import windll
    # 设置进程为 Per-Monitor DPI 感知 (Windows 10/11 4K 屏必备)
    # 必须在 root = tk.Tk() 之前生效
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        windll.user32.SetProcessDPIAware()
    except Exception:
        pass
# --- DPI 设置结束 ---


class Chapter:
    """章节类"""
    def __init__(self, title: str, start_pos: int, end_pos: int = None):
        self.title = title.strip()
        self.start_pos = start_pos
        self.end_pos = end_pos
    
    def __repr__(self):
        return f"Chapter('{self.title}', {self.start_pos}, {self.end_pos})"


class TXTSplitter:
    """TXT文档拆分器主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("TXT文档拆分工具")
        
        # [修复 1] 必须先加载设置
        self.settings = self.load_settings()
        
        # [修复 2] 优化 DPI 缩放逻辑
        self.dpi_scale = 1.0 # 默认值
        if sys.platform == 'win32':
            try:
                from ctypes import windll
                try:
                    hdc = windll.user32.GetDC(0)
                    logical_dpi = windll.gdi32.GetDeviceCaps(hdc, 88) # LOGPIXELSX
                    windll.user32.ReleaseDC(0, hdc)
                    calc_scale = logical_dpi / 96.0
                    # 限制范围防止计算错误导致界面过大
                    if 0.8 < calc_scale < 3.0:
                        self.dpi_scale = calc_scale
                    else:
                        self.dpi_scale = 1.0
                except:
                    self.dpi_scale = 1.0
            except:
                self.dpi_scale = 1.0
        
        # 应用用户设置的UI缩放
        self.ui_scale = self.settings.get('ui_scale', 1.0)
        self.font_scale = self.settings.get('font_scale', 1.0)
        
        # 根据DPI调整窗口大小
        base_width, base_height = 1000, 750
        width = int(base_width * self.dpi_scale)
        height = int(base_height * self.dpi_scale)
        self.root.geometry(f"{width}x{height}")
        
        # 设置最小窗口大小
        self.root.minsize(int(800 * self.dpi_scale), int(600 * self.dpi_scale))
        
        # 现代简约配色
        self.colors = {
            'bg': '#FAFAFA',
            'fg': '#2C2C2E',
            'frame_bg': '#FFFFFF',
            'accent': '#007AFF',
            'accent_hover': '#0051D5',
            'border': '#E5E5EA',
            'selected': '#E3F2FD',
            'button_bg': '#007AFF',
            'button_fg': '#FFFFFF',
            'secondary_bg': '#F2F2F7',
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        self.file_path = None
        self.file_content = ""
        self.chapters: List[Chapter] = []
        self.selected_chapters = []
        
        self.setup_styles()
        self.setup_ui()
    
    def load_settings(self):
        """加载用户设置"""
        # [修复 3] 兼容 PyInstaller 打包路径
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        
        settings_file = os.path.join(base_path, 'settings.json')
        default_settings = {
            'font_scale': 1.0,
            'ui_scale': 1.0
        }
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    user_settings = json.load(f)
                    default_settings.update(user_settings)
            except:
                pass
        
        return default_settings
    
    def save_settings(self):
        """保存用户设置"""
        # [修复 3] 兼容 PyInstaller 打包路径
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
            
        settings_file = os.path.join(base_path, 'settings.json')
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def setup_styles(self):
        """设置苹果风格的样式"""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass
        
        # 字体大小计算
        base_font_size = 8
        title_font_size = 9
        small_font_size = 7
        font_size = max(8, int(base_font_size * self.dpi_scale * self.font_scale))
        title_size = max(9, int(title_font_size * self.dpi_scale * self.font_scale))
        small_size = max(7, int(small_font_size * self.dpi_scale * self.font_scale))
        
        # Padding 计算
        base_padding = 12
        base_padding_small = 6
        padding = int(base_padding * self.dpi_scale * self.ui_scale)
        padding_small = int(base_padding_small * self.dpi_scale * self.ui_scale)
        
        # 配置Frame样式
        style.configure('Card.TFrame', 
                       background=self.colors['frame_bg'],
                       relief='flat',
                       borderwidth=0)
        
        style.configure('Card.TLabelframe',
                       background=self.colors['frame_bg'],
                       foreground=self.colors['fg'],
                       borderwidth=1,
                       relief='flat',
                       bordercolor=self.colors['border'])
        
        style.configure('Card.TLabelframe.Label',
                       background=self.colors['frame_bg'],
                       foreground=self.colors['fg'],
                       font=('Segoe UI', title_size))
        
        style.configure('Card.TLabel',
                      background=self.colors['frame_bg'],
                      foreground=self.colors['fg'],
                      font=('Segoe UI', font_size))
        
        style.configure('Primary.TButton',
                      background=self.colors['button_bg'],
                      foreground=self.colors['button_fg'],
                      borderwidth=0,
                      focuscolor='none',
                      font=('Segoe UI', font_size),
                      padding=(int(10 * self.dpi_scale * self.ui_scale), 
                              int(4 * self.dpi_scale * self.ui_scale)))
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['accent_hover']),
                           ('pressed', self.colors['accent_hover'])])
        
        style.configure('Secondary.TButton',
                       background=self.colors['secondary_bg'],
                       foreground=self.colors['fg'],
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', font_size),
                       padding=(int(8 * self.dpi_scale * self.ui_scale), 
                               int(4 * self.dpi_scale * self.ui_scale)))
        
        style.map('Secondary.TButton',
                 background=[('active', '#E5E5EA'),
                           ('pressed', '#D1D1D6')])
        
        style.configure('Card.TEntry',
                       fieldbackground=self.colors['frame_bg'],
                       foreground=self.colors['fg'],
                       borderwidth=1,
                       relief='flat',
                       bordercolor=self.colors['border'],
                       padding=int(4 * self.dpi_scale * self.ui_scale),
                       font=('Segoe UI', font_size))
        
        style.configure('Card.TRadiobutton',
                      background=self.colors['frame_bg'],
                      foreground=self.colors['fg'],
                      font=('Segoe UI', font_size),
                      focuscolor='none')
        
        style.configure('Card.TCheckbutton',
                       background=self.colors['frame_bg'],
                       foreground=self.colors['fg'],
                       font=('Segoe UI', font_size),
                       focuscolor='none')
        
        style.configure('Status.TLabel',
                      background=self.colors['secondary_bg'],
                      foreground=self.colors['fg'],
                      font=('Segoe UI', small_size),
                      padding=int(4 * self.dpi_scale),
                      relief='flat')
    
    def setup_ui(self):
        """设置用户界面"""
        main_padx = int(12 * self.dpi_scale * self.ui_scale)
        main_pady = int(12 * self.dpi_scale * self.ui_scale)
        main_frame = tk.Frame(self.root, bg=self.colors['bg'], padx=main_padx, pady=main_pady)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        file_padding = int(12 * self.dpi_scale * self.ui_scale)
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", 
                                   style='Card.TLabelframe', padding=str(file_padding))
        file_pady = int(10 * self.dpi_scale * self.ui_scale)
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, file_pady))
        
        file_inner = ttk.Frame(file_frame, style='Card.TFrame')
        file_inner.pack(fill=tk.BOTH, expand=True)
        
        font_size = max(8, int(8 * self.dpi_scale * self.font_scale))
        self.file_label = ttk.Label(file_inner, text="未选择文件", 
                                   style='Card.TLabel', font=('Segoe UI', font_size))
        pad_val = int(10 * self.dpi_scale * self.ui_scale)
        pady_val = int(3 * self.dpi_scale * self.ui_scale)
        self.file_label.grid(row=0, column=0, sticky=tk.W, padx=(0, pad_val), pady=pady_val)
        
        ttk.Button(file_inner, text="选择文件", command=self.select_file,
                  style='Primary.TButton').grid(row=0, column=1, padx=pady_val, pady=pady_val)
        
        ttk.Button(file_inner, text="识别章节", command=self.detect_chapters,
                  style='Primary.TButton').grid(row=0, column=2, padx=pady_val, pady=pady_val)
        
        chapter_frame = ttk.LabelFrame(main_frame, text="章节列表", 
                                      style='Card.TLabelframe', padding="12")
        chapter_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        chapter_inner = ttk.Frame(chapter_frame, style='Card.TFrame')
        chapter_inner.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(chapter_inner, style='Card.TFrame')
        btn_frame.pack(fill=tk.X, pady=(0, 6))
        
        ttk.Button(btn_frame, text="全选", command=self.select_all,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="全不选", command=self.deselect_all,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="反选", command=self.invert_selection,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=2)
        
        list_frame = tk.Frame(chapter_inner, bg=self.colors['frame_bg'], 
                             highlightbackground=self.colors['border'],
                             highlightthickness=1)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 2), pady=2)
        
        listbox_font_size = max(8, int(8 * self.dpi_scale * self.font_scale))
        self.chapter_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, 
                                          yscrollcommand=scrollbar.set,
                                          height=15,
                                          bg=self.colors['frame_bg'],
                                          fg=self.colors['fg'],
                                          selectbackground=self.colors['accent'],
                                          selectforeground='#FFFFFF',
                                          borderwidth=0,
                                          highlightthickness=0,
                                          font=('Segoe UI', listbox_font_size),
                                          activestyle='none')
        self.chapter_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        scrollbar.config(command=self.chapter_listbox.yview)
        
        export_frame = ttk.LabelFrame(main_frame, text="导出选项", 
                                     style='Card.TLabelframe', padding="12")
        export_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        export_inner = ttk.Frame(export_frame, style='Card.TFrame')
        export_inner.pack(fill=tk.BOTH, expand=True)
        
        split_frame = ttk.Frame(export_inner, style='Card.TFrame')
        split_frame.pack(fill=tk.X, pady=(0, 10))
        
        label_font_size = max(8, int(8 * self.dpi_scale * self.font_scale))
        ttk.Label(split_frame, text="分割方式", style='Card.TLabel',
                 font=('Segoe UI', label_font_size)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.split_mode = tk.StringVar(value="chapter")
        ttk.Radiobutton(split_frame, text="按章节", variable=self.split_mode, 
                       value="chapter", command=self.on_split_mode_changed,
                       style='Card.TRadiobutton').pack(side=tk.LEFT, padx=8)
        ttk.Radiobutton(split_frame, text="按大小", variable=self.split_mode, 
                       value="size", command=self.on_split_mode_changed,
                       style='Card.TRadiobutton').pack(side=tk.LEFT, padx=8)
        
        size_frame = ttk.Frame(export_inner, style='Card.TFrame')
        size_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(size_frame, text="文件大小", style='Card.TLabel',
                 font=('Segoe UI', label_font_size)).pack(side=tk.LEFT, padx=(0, 6))
        self.size_entry = ttk.Entry(size_frame, width=10, style='Card.TEntry')
        self.size_entry.insert(0, "100000")
        self.size_entry.pack(side=tk.LEFT, padx=3)
        ttk.Label(size_frame, text="字符", style='Card.TLabel',
                 font=('Segoe UI', label_font_size)).pack(side=tk.LEFT, padx=(3, 0))
        
        format_frame = ttk.Frame(export_inner, style='Card.TFrame')
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(format_frame, text="输出格式", style='Card.TLabel',
                 font=('Segoe UI', label_font_size)).pack(side=tk.LEFT, padx=(0, 10))
        self.output_format = tk.StringVar(value="txt")
        ttk.Radiobutton(format_frame, text="TXT", variable=self.output_format, 
                       value="txt", style='Card.TRadiobutton').pack(side=tk.LEFT, padx=8)
        ttk.Radiobutton(format_frame, text="Markdown", variable=self.output_format, 
                       value="md", style='Card.TRadiobutton').pack(side=tk.LEFT, padx=8)
        
        merge_frame = ttk.Frame(export_inner, style='Card.TFrame')
        merge_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.merge_export = tk.BooleanVar(value=False)
        self.merge_check = ttk.Checkbutton(merge_frame, 
                                         text="合并导出到单个文件", 
                                         variable=self.merge_export,
                                         style='Card.TCheckbutton')
        self.merge_check.pack(side=tk.LEFT)
        
        button_frame = ttk.Frame(export_inner, style='Card.TFrame')
        button_frame.pack(fill=tk.X, pady=(6, 0))
        
        ttk.Button(button_frame, text="导出选中", command=self.export_selected,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=4)
        ttk.Button(button_frame, text="导出全部", command=self.export_all,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=4)
        
        bottom_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        bottom_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 0))
        
        settings_btn = ttk.Button(bottom_frame, text="⚙ 设置", 
                                 command=self.open_settings,
                                 style='Secondary.TButton')
        settings_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_label = ttk.Label(bottom_frame, text="就绪", style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        self.on_split_mode_changed()
    
    def open_settings(self):
        """打开设置窗口"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("界面设置")
        # 简单设置大小，不随 DPI 过度缩放导致窗口过大
        settings_window.geometry("400x300") 
        settings_window.configure(bg=self.colors['bg'])
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # 居中显示
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() // 2) - (settings_window.winfo_width() // 2)
        y = (settings_window.winfo_screenheight() // 2) - (settings_window.winfo_height() // 2)
        settings_window.geometry(f"+{x}+{y}")
        
        main_frame = tk.Frame(settings_window, bg=self.colors['bg'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        font_frame = ttk.LabelFrame(main_frame, text="字体大小", 
                                   style='Card.TLabelframe', padding="15")
        font_frame.pack(fill=tk.X, pady=(0, 15))
        
        font_inner = ttk.Frame(font_frame, style='Card.TFrame')
        font_inner.pack(fill=tk.X)
        
        ttk.Label(font_inner, text="字体缩放:", style='Card.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        font_scale_var = tk.DoubleVar(value=self.font_scale)
        font_scale_scale = ttk.Scale(font_inner, from_=0.7, to=1.5, 
                                    variable=font_scale_var, orient=tk.HORIZONTAL, length=200)
        font_scale_scale.pack(side=tk.LEFT, padx=10)
        
        font_value_label = ttk.Label(font_inner, text=f"{self.font_scale:.2f}", 
                                     style='Card.TLabel', width=5)
        font_value_label.pack(side=tk.LEFT, padx=5)
        
        def update_font_value(val):
            font_value_label.config(text=f"{float(val):.2f}")
        
        font_scale_scale.config(command=update_font_value)
        
        ui_frame = ttk.LabelFrame(main_frame, text="界面大小", 
                                 style='Card.TLabelframe', padding="15")
        ui_frame.pack(fill=tk.X, pady=(0, 15))
        
        ui_inner = ttk.Frame(ui_frame, style='Card.TFrame')
        ui_inner.pack(fill=tk.X)
        
        ttk.Label(ui_inner, text="界面缩放:", style='Card.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        ui_scale_var = tk.DoubleVar(value=self.ui_scale)
        ui_scale_scale = ttk.Scale(ui_inner, from_=0.8, to=1.5, 
                                   variable=ui_scale_var, orient=tk.HORIZONTAL, length=200)
        ui_scale_scale.pack(side=tk.LEFT, padx=10)
        
        ui_value_label = ttk.Label(ui_inner, text=f"{self.ui_scale:.2f}", 
                                  style='Card.TLabel', width=5)
        ui_value_label.pack(side=tk.LEFT, padx=5)
        
        def update_ui_value(val):
            ui_value_label.config(text=f"{float(val):.2f}")
        
        ui_scale_scale.config(command=update_ui_value)
        
        info_label = ttk.Label(main_frame, 
                              text="提示：修改设置后需要重启程序才能生效",
                              style='Card.TLabel',
                              foreground='#666666')
        info_label.pack(pady=10)
        
        btn_frame = ttk.Frame(main_frame, style='Card.TFrame')
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        def save_and_close():
            self.settings['font_scale'] = font_scale_var.get()
            self.settings['ui_scale'] = ui_scale_var.get()
            self.save_settings()
            messagebox.showinfo("设置已保存", "设置已保存！请重启程序使设置生效。")
            settings_window.destroy()
        
        ttk.Button(btn_frame, text="保存", command=save_and_close,
                  style='Primary.TButton').pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=settings_window.destroy,
                  style='Secondary.TButton').pack(side=tk.RIGHT, padx=5)
    
    def on_split_mode_changed(self):
        """分割模式改变时的回调"""
        if self.split_mode.get() == "size":
            self.merge_check.config(state='disabled')
            self.merge_export.set(False)
        else:
            self.merge_check.config(state='normal')
    
    def select_file(self):
        """选择TXT文件"""
        file_path = filedialog.askopenfilename(
            title="选择TXT文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path = file_path
            self.file_label.config(text=f"已选择: {os.path.basename(file_path)}")
            try:
                encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5']
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            self.file_content = f.read()
                        self.status_label.config(text=f"文件加载成功 (编码: {encoding})")
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    messagebox.showerror("错误", "无法读取文件，编码不支持")
            except Exception as e:
                messagebox.showerror("错误", f"读取文件失败: {str(e)}")
    
    def detect_chapters(self):
        """识别章节"""
        if not self.file_content:
            messagebox.showwarning("警告", "请先选择文件")
            return
        
        self.chapters = []
        
        patterns = [
            r'^第\s*[一二三四五六七八九十百千万\d]+\s*章[^\n]*',
            r'^第\s*[一二三四五六七八九十百千万\d]+\s*节[^\n]*',
            r'^第[一二三四五六七八九十百千万\d]+章[^\n]*',
            r'^第[一二三四五六七八九十百千万\d]+节[^\n]*',
            r'^Chapter\s+\d+[^\n]*',
            r'^CHAPTER\s+\d+[^\n]*',
            r'^第[一二三四五六七八九十百千万\d]+回[^\n]*',
            r'^第\s*[一二三四五六七八九十百千万\d]+\s*回[^\n]*',
            r'^第[一二三四五六七八九十百千万\d]+集[^\n]*',
            r'^第\s*[一二三四五六七八九十百千万\d]+\s*集[^\n]*',
            r'^\d+[\.、]\s*[^\n]*',
            r'^【第[一二三四五六七八九十百千万\d]+章】[^\n]*',
            r'^【第\s*[一二三四五六七八九十百千万\d]+\s*章】[^\n]*',
            r'^【第[一二三四五六七八九十百千万\d]+节】[^\n]*',
            r'^【第\s*[一二三四五六七八九十百千万\d]+\s*节】[^\n]*',
        ]
        
        lines = self.file_content.split('\n')
        current_pos = 0
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                current_pos += len(line) + 1
                continue
            
            for pattern in patterns:
                if re.match(pattern, line_stripped):
                    chapter = Chapter(line_stripped, current_pos)
                    self.chapters.append(chapter)
                    break
            
            current_pos += len(line) + 1
        
        for i in range(len(self.chapters)):
            if i < len(self.chapters) - 1:
                self.chapters[i].end_pos = self.chapters[i + 1].start_pos
            else:
                self.chapters[i].end_pos = len(self.file_content)
        
        self.chapter_listbox.delete(0, tk.END)
        for chapter in self.chapters:
            self.chapter_listbox.insert(tk.END, chapter.title)
        
        self.status_label.config(text=f"识别到 {len(self.chapters)} 个章节")
        
        if len(self.chapters) == 0:
            messagebox.showinfo("提示", "未识别到章节，您可以手动选择内容进行导出")
    
    def select_all(self):
        """全选章节"""
        self.chapter_listbox.selection_set(0, tk.END)
    
    def deselect_all(self):
        """全不选"""
        self.chapter_listbox.selection_clear(0, tk.END)
    
    def invert_selection(self):
        """反选"""
        selected = set(self.chapter_listbox.curselection())
        for i in range(self.chapter_listbox.size()):
            if i in selected:
                self.chapter_listbox.selection_clear(i)
            else:
                self.chapter_listbox.selection_set(i)
    
    def export_selected(self):
        """导出选中的章节"""
        selected_indices = self.chapter_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("警告", "请至少选择一个章节")
            return
        
        if not self.chapters:
            messagebox.showwarning("警告", "未识别到章节，请先识别章节")
            return
        
        self._export_chapters([self.chapters[i] for i in selected_indices])
    
    def export_all(self):
        """导出所有章节"""
        if not self.chapters:
            messagebox.showwarning("警告", "未识别到章节，请先识别章节")
            return
        
        self._export_chapters(self.chapters)
    
    def _export_chapters(self, chapters_to_export: List[Chapter]):
        """导出章节的内部方法"""
        if not chapters_to_export:
            return
        
        output_dir = filedialog.askdirectory(title="选择输出目录")
        if not output_dir:
            return
        
        split_mode = self.split_mode.get()
        output_format = self.output_format.get()
        merge_export = self.merge_export.get()
        
        # 获取原文件名（不含后缀），用于生成新文件名
        base_filename = "未命名文档"
        if self.file_path:
            base_filename = os.path.splitext(os.path.basename(self.file_path))[0]
        
        try:
            if split_mode == "chapter":
                if merge_export:
                    self._export_merged(chapters_to_export, output_dir, output_format, base_filename)
                else:
                    self._export_by_chapter(chapters_to_export, output_dir, output_format, base_filename)
            else:
                size_limit = int(self.size_entry.get())
                self._export_by_size(chapters_to_export, output_dir, output_format, size_limit, base_filename)
            
            if merge_export:
                messagebox.showinfo("成功", f"已合并导出 {len(chapters_to_export)} 个章节到: {output_dir}")
                self.status_label.config(text=f"导出完成: 1 个合并文件")
            else:
                messagebox.showinfo("成功", f"已导出 {len(chapters_to_export)} 个章节到: {output_dir}")
                self.status_label.config(text=f"导出完成: {len(chapters_to_export)} 个文件")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
            self.status_label.config(text="导出失败")
    
    def _ask_filename(self, initial_name: str) -> Optional[str]:
        """
        弹出对话框询问文件名，支持修改
        返回用户输入的文件名，如果取消则返回 None
        """
        # 创建自定义对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("输入文件名")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(dialog, text="请输入导出文件的名称：", font=('Segoe UI', 10)).pack(pady=(20, 5))
        
        name_var = tk.StringVar(value=initial_name)
        entry = tk.Entry(dialog, textvariable=name_var, font=('Segoe UI', 10), width=40)
        entry.pack(pady=5)
        entry.select_range(0, tk.END)
        entry.focus()
        
        result = [None]
        
        def on_ok():
            result[0] = name_var.get().strip()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="确定", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="取消", command=on_cancel, width=10).pack(side=tk.LEFT, padx=10)
        
        # 绑定回车键
        dialog.bind('<Return>', lambda event: on_ok())
        dialog.bind('<Escape>', lambda event: on_cancel())
        
        self.root.wait_window(dialog)
        return result[0]

    def _remove_title_from_content(self, content: str, title: str) -> str:
        """从内容开头移除章节标题（如果存在）"""
        lines = content.split('\n')
        if not lines:
            return content
        
        first_line = lines[0].strip()
        title_stripped = title.strip()
        
        if first_line == title_stripped:
            if len(lines) > 1:
                return '\n'.join(lines[1:])
            else:
                return ''
        
        return content
    
    def _export_by_chapter(self, chapters: List[Chapter], output_dir: str, format_type: str, base_name: str):
        """按章节导出（分别导出）"""
        for i, chapter in enumerate(chapters, 1):
            content = self.file_content[chapter.start_pos:chapter.end_pos]
            
            # 获取该章节在整个文档中的索引，以便生成 1~10 这样的范围
            try:
                global_index = self.chapters.index(chapter) + 1
            except ValueError:
                global_index = i
            
            if format_type == "md":
                content = self._remove_title_from_content(content, chapter.title)
                content = f"# {chapter.title}\n\n{content}"
                ext = ".md"
            else:
                ext = ".txt"
            
            # 生成默认文件名
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', chapter.title)
            # 限制章节标题长度，防止文件名过长
            if len(safe_title) > 30:
                safe_title = safe_title[:30]
            
            # 拼接文件名：原名 - 索引_标题
            default_filename = f"{base_name}-{global_index:04d}_{safe_title}{ext}"
            
            # 询问用户修改文件名 (仅针对第一个文件弹出，后续如果全部用同一个名字逻辑会不同，这里简单处理为每次都问，或者只问第一个)
            # 为了体验流畅，这里我们只在第一个文件时弹出询问，或者不弹直接按规则生成。
            # 题目要求“支持修改”，这里我们弹窗让用户确认第一个文件名，
            # 如果是批量导出，后面的文件按规律生成不再弹窗（避免点击太多次）。
            # 特殊情况：如果只导出一个文件，则完全允许修改。
            
            if i == 1:
                user_filename = self._ask_filename(default_filename)
                if not user_filename: # 用户取消
                    # 恢复默认名称并继续，还是直接中断？通常中断比较好
                    # 但这里为了方便，如果取消，使用默认名
                    final_filename = default_filename
                else:
                    # 确保扩展名正确
                    if not user_filename.endswith(ext):
                        user_filename += ext
                    # 清理非法字符
                    user_filename = re.sub(r'[<>:"/\\|?*]', '_', user_filename)
                    final_filename = user_filename
                    
                    # 如果用户修改了主名称，我们需要记录这个前缀用于后续文件吗？
                    # 题目举例是“制霸好莱坞-1~10”，如果是分别导出，通常是“制霸 Hollywood-0001_标题”。
                    # 这里我们假定用户修改的是这一个特定文件的名称。
            else:
                # 后续文件不再弹窗，自动生成
                final_filename = default_filename
            
            filepath = os.path.join(output_dir, final_filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def _export_merged(self, chapters: List[Chapter], output_dir: str, format_type: str, base_name: str):
        """合并导出到单个文件"""
        merged_content = []
        
        for chapter in chapters:
            chapter_content = self.file_content[chapter.start_pos:chapter.end_pos]
            chapter_content = self._remove_title_from_content(chapter_content, chapter.title)
            merged_content.append(f"# {chapter.title}\n\n{chapter_content}")
        
        final_content = "\n\n".join(merged_content)
        
        if format_type == "md":
            ext = ".md"
        else:
            ext = ".txt"
        
        # 获取范围索引
        start_idx = 1
        end_idx = len(self.chapters)
        if chapters[0] in self.chapters:
            start_idx = self.chapters.index(chapters[0]) + 1
        if chapters[-1] in self.chapters:
            end_idx = self.chapters.index(chapters[-1]) + 1
            
        # 生成默认文件名：原名 - 起始~结束
        default_filename = f"{base_name}-{start_idx}~{end_idx}{ext}"
        
        # 弹窗询问文件名
        user_filename = self._ask_filename(default_filename)
        
        if user_filename:
            if not user_filename.endswith(ext):
                user_filename += ext
            # 清理非法字符
            user_filename = re.sub(r'[<>:"/\\|?*]', '_', user_filename)
            filename = user_filename
        else:
            # 用户取消，使用默认名
            filename = default_filename
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)

    def _export_by_size(self, chapters: List[Chapter], output_dir: str, format_type: str, size_limit: int, base_name: str):
        """按大小分割导出"""
        current_content = ""
        current_size = 0
        file_index = 1
        
        for chapter in chapters:
            chapter_content = self.file_content[chapter.start_pos:chapter.end_pos]
            
            if format_type == "md":
                chapter_content = self._remove_title_from_content(chapter_content, chapter.title)
                chapter_title = f"# {chapter.title}\n\n"
                chapter_text = chapter_title + chapter_content
            else:
                chapter_text = chapter_content
            
            chapter_size = len(chapter_text)
            
            if chapter_size > size_limit:
                if current_content:
                    default_filename = f"{base_name}-part_{file_index:04d}.{format_type}"
                    # 第一个文件弹窗询问
                    if file_index == 1:
                        user_input = self._ask_filename(default_filename)
                        if user_input:
                            if not user_input.endswith(f".{format_type}"): user_input += f".{format_type}"
                            default_filename = re.sub(r'[<>:"/\\|?*]', '_', user_input)
                    
                    filepath = os.path.join(output_dir, default_filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(current_content)
                    file_index += 1
                    current_content = ""
                    current_size = 0
                
                safe_title = re.sub(r'[<>:"/\\|?*]', '_', chapter.title)
                # 超大单章文件名：原名-part_index_标题
                default_filename = f"{base_name}-part_{file_index:04d}_{safe_title}.{format_type}"
                
                filepath = os.path.join(output_dir, default_filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(chapter_text)
                file_index += 1
            else:
                if current_size + chapter_size > size_limit and current_content:
                    default_filename = f"{base_name}-part_{file_index:04d}.{format_type}"
                    # 第一个文件弹窗询问
                    if file_index == 1:
                        user_input = self._ask_filename(default_filename)
                        if user_input:
                            if not user_input.endswith(f".{format_type}"): user_input += f".{format_type}"
                            default_filename = re.sub(r'[<>:"/\\|?*]', '_', user_input)
                    
                    filepath = os.path.join(output_dir, default_filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(current_content)
                    file_index += 1
                    current_content = chapter_text
                    current_size = chapter_size
                else:
                    if current_content:
                        current_content += "\n\n" + chapter_text
                    else:
                        current_content = chapter_text
                    current_size = len(current_content)
        
        if current_content:
            default_filename = f"{base_name}-part_{file_index:04d}.{format_type}"
            # 第一个文件弹窗询问
            if file_index == 1:
                user_input = self._ask_filename(default_filename)
                if user_input:
                    if not user_input.endswith(f".{format_type}"): user_input += f".{format_type}"
                    default_filename = re.sub(r'[<>:"/\\|?*]', '_', user_input)
            
            filepath = os.path.join(output_dir, default_filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(current_content)


def main():
    """主函数"""
    root = tk.Tk()
    app = TXTSplitter(root)
    root.mainloop()


if __name__ == "__main__":
    main()