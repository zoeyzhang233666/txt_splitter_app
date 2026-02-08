#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import os

# --- 电子书支持 ---
try:
    from ebooklib import epub
    from bs4 import BeautifulSoup
    import mobi
    EBOOK_SUPPORT = True
except ImportError:
    EBOOK_SUPPORT = False

# --- 拖拽支持 (新增) ---
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_SUPPORT = True
except ImportError:
    DND_SUPPORT = False
    print("提示: 未安装 tkinterdnd2，拖拽功能不可用。请运行 pip install tkinterdnd2")

# --- DPI 适配 ---
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

class Chapter:
    def __init__(self, title: str, start_pos: int, end_pos: int = None):
        self.title = title.strip()
        self.start_pos = start_pos
        self.end_pos = end_pos

class ScrollableCheckBoxFrame(tk.Frame):
    """自定义滚动勾选列表组件"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def clear(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

class TXTSplitter:
    def __init__(self, root):
        self.root = root
        self.root.title("文档拆分工具 - 加强版")
        self.root.geometry("1100x900")
        
        self.file_path = ""
        self.file_name_stem = ""
        self.file_content = ""
        self.chapters = []
        self.check_vars = [] 

        # 配置变量
        self.use_file_prefix = tk.BooleanVar(value=True)
        self.use_index_prefix = tk.BooleanVar(value=False)
        self.split_size_mb = tk.StringVar(value="1.0")
        self.merge_count = tk.StringVar(value="10")
        self.output_ext = tk.StringVar(value="txt")
        
        # --- 注册拖拽 (新增) ---
        if DND_SUPPORT:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.drop_file)
        
        self.setup_ui()

    def setup_ui(self):
        self.root.configure(bg='#F8F9FA')
        main_frame = tk.Frame(self.root, bg='#F8F9FA', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. 文件加载
        f_frame = ttk.LabelFrame(main_frame, text=" 1. 文件加载 ", padding=10)
        f_frame.pack(fill=tk.X, pady=5)
        
        # 修改提示文本
        hint_text = "支持格式: TXT, Epub, Mobi"
        if DND_SUPPORT: hint_text += " (支持文件拖入)"
        
        self.file_label = ttk.Label(f_frame, text=hint_text)
        self.file_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(f_frame, text="打开文件", command=self.load_file).pack(side=tk.RIGHT, padx=5)
        ttk.Button(f_frame, text="识别章节", command=self.detect_chapters).pack(side=tk.RIGHT, padx=5)

        # 2. 章节预览
        l_frame = ttk.LabelFrame(main_frame, text=" 2. 章节列表 ", padding=10)
        l_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        btn_bar = tk.Frame(l_frame, bg='white')
        btn_bar.pack(fill=tk.X)
        ttk.Button(btn_bar, text="全选", command=self.select_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_bar, text="反选", command=self.invert_selection).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_bar, text="清空", command=self.select_none).pack(side=tk.LEFT, padx=2)

        self.chapter_area = ScrollableCheckBoxFrame(l_frame)
        self.chapter_area.pack(fill=tk.BOTH, expand=True, pady=5)

        # 3. 命名规则
        n_frame = ttk.LabelFrame(main_frame, text=" 3. 命名与格式设置 ", padding=10)
        n_frame.pack(fill=tk.X, pady=5)
        tk.Checkbutton(n_frame, text="包含原文件名", variable=self.use_file_prefix, bg='#F8F9FA').pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(n_frame, text="包含序号 (0001_)", variable=self.use_index_prefix, bg='#F8F9FA').pack(side=tk.LEFT, padx=10)
        
        ttk.Separator(n_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=15)
        ttk.Label(n_frame, text="导出后缀:").pack(side=tk.LEFT)
        ttk.Radiobutton(n_frame, text="TXT", variable=self.output_ext, value="txt").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(n_frame, text="Markdown", variable=self.output_ext, value="md").pack(side=tk.LEFT, padx=5)

        # 4. 导出动作
        e_frame = ttk.LabelFrame(main_frame, text=" 4. 导出模式 ", padding=10)
        e_frame.pack(fill=tk.X, pady=5)

        row1 = tk.Frame(e_frame); row1.pack(fill=tk.X, pady=2)
        ttk.Button(row1, text="导出勾选项：一章一档", command=self.export_individual).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1, text="导出勾选项：合并为单档", command=self.export_merged_single).pack(side=tk.LEFT, padx=5)

        row2 = tk.Frame(e_frame); row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="按大小分割 (MB):").pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.split_size_mb, width=6).pack(side=tk.LEFT, padx=5)
        ttk.Button(row2, text="执行分割导出", command=self.export_by_size).pack(side=tk.LEFT, padx=5)

        row3 = tk.Frame(e_frame); row3.pack(fill=tk.X, pady=2)
        ttk.Label(row3, text="每 ").pack(side=tk.LEFT)
        ttk.Entry(row3, textvariable=self.merge_count, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Label(row3, text=" 章节合并导出").pack(side=tk.LEFT)
        ttk.Button(row3, text="执行批量合并", command=self.export_by_count).pack(side=tk.LEFT, padx=5)

    # --- 逻辑实现 ---

    # 新增: 拖拽事件处理
    def drop_file(self, event):
        path = event.data
        if not path: return
        
        # 兼容处理：Windows下拖拽如果路径有空格，会被{}包裹
        # 使用简单的正则提取第一个文件路径
        paths = re.findall(r'\{.*?\}|\S+', path)
        if paths:
            # 取第一个文件，去除可能存在的花括号
            first_path = paths[0].strip('{}')
            self.load_file_by_path(first_path)

    # 修改: 仅保留对话框逻辑，调用 load_file_by_path
    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("支持格式", "*.txt;*.epub;*.mobi")])
        if not path: return
        self.load_file_by_path(path)

    # 新增: 核心读取逻辑（从 load_file 剥离）
    def load_file_by_path(self, path):
        self.file_path = path
        self.file_name_stem = os.path.splitext(os.path.basename(path))[0]
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".txt":
                # 尝试多种编码
                for enc in ['utf-8-sig', 'gb18030', 'gbk', 'utf-16']:
                    try:
                        with open(path, 'r', encoding=enc) as f: 
                            self.file_content = f.read()
                            break
                    except: continue
            elif ext == ".epub" and EBOOK_SUPPORT:
                book = epub.read_epub(path)
                self.file_content = "\n\n".join([BeautifulSoup(i.get_content(), 'html.parser').get_text() for i in book.get_items() if i.get_type()==9])
            elif ext == ".mobi" and EBOOK_SUPPORT:
                _, res_path = mobi.extract(path)
                with open(res_path, 'r', encoding='utf-8', errors='ignore') as f:
                    self.file_content = BeautifulSoup(f.read(), 'html.parser').get_text()
            else:
                if ext not in [".txt", ".epub", ".mobi"]:
                    messagebox.showerror("错误", "不支持的文件格式")
                    return

            self.file_label.config(text=f"已载入: {os.path.basename(path)}")
            # 自动触发一次章节识别，方便用户
            self.detect_chapters()
            
        except Exception as e: messagebox.showerror("错误", f"读取失败: {str(e)}")

    def detect_chapters(self):
        if not self.file_content: return
        patterns = [r'^\s*第\s*[一二三四五六七八九十百千万\d]+\s*[章节回集].*$', r'^\s*Chapter\s+\d+.*$', r'^\s*\d+[\.、\s].*$']
        regex = re.compile('|'.join(patterns), re.MULTILINE)
        self.chapters = [Chapter(m.group(), m.start()) for m in regex.finditer(self.file_content)]
        for i in range(len(self.chapters)):
            self.chapters[i].end_pos = self.chapters[i+1].start_pos if i < len(self.chapters)-1 else len(self.file_content)
        self.refresh_chapter_list()
        if not self.chapters:
            messagebox.showinfo("提示", "未自动识别到章节，请确认文档格式")

    def refresh_chapter_list(self):
        self.chapter_area.clear()
        self.check_vars = []
        for c in self.chapters:
            var = tk.BooleanVar(value=True)
            cb = tk.Checkbutton(self.chapter_area.scrollable_frame, text=c.title, variable=var, bg='white', anchor='w')
            cb.pack(fill=tk.X, padx=5, pady=1)
            self.check_vars.append(var)

    def select_all(self): [v.set(True) for v in self.check_vars]
    def select_none(self): [v.set(False) for v in self.check_vars]
    def invert_selection(self): [v.set(not v.get()) for v in self.check_vars]

    def _prepare_content(self, chapter):
        """MD去重逻辑"""
        raw_text = self.file_content[chapter.start_pos:chapter.end_pos].strip()
        if self.output_ext.get() == "md":
            lines = raw_text.split('\n')
            if lines and lines[0].strip().lower() == chapter.title.lower():
                body = "\n".join(lines[1:]).strip()
            else: body = raw_text
            return f"# {chapter.title}\n\n{body}"
        return raw_text

    def _get_filename(self, idx, title):
        """通用单章/片段命名逻辑"""
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title).strip()
        parts = []
        if self.use_file_prefix.get(): parts.append(self.file_name_stem)
        if self.use_index_prefix.get(): parts.append(f"{idx:04d}")
        parts.append(safe_title)
        return "_".join(parts) + f".{self.output_ext.get()}"

    def get_selected_chapters(self):
        return [(i, self.chapters[i]) for i, v in enumerate(self.check_vars) if v.get()]

    # --- 导出方法 ---

    def export_individual(self):
        selected = self.get_selected_chapters()
        if not selected: return
        out_dir = filedialog.askdirectory()
        if not out_dir: return
        for idx, chapter in selected:
            content = self._prepare_content(chapter)
            name = self._get_filename(idx+1, chapter.title)
            with open(os.path.join(out_dir, name), 'w', encoding='utf-8') as f: f.write(content)
        messagebox.showinfo("完成", f"已成功导出 {len(selected)} 个文件")

    def export_merged_single(self):
        selected_data = self.get_selected_chapters()
        if not selected_data: return
        
        default_name = self._get_filename(0, "合并导出").replace("_0000", "") 
        
        save_path = filedialog.asksaveasfilename(
            title="保存合并文件",
            defaultextension=f".{self.output_ext.get()}",
            initialfile=default_name,
            filetypes=[("文档", f"*.{self.output_ext.get()}")])
            
        if not save_path: return
        with open(save_path, 'w', encoding='utf-8') as f:
            for _, c in selected_data: 
                f.write(self._prepare_content(c) + "\n\n---\n\n")
        messagebox.showinfo("完成", "合并文件导出成功")

    def export_by_size(self):
        if not self.chapters: return
        try: limit = float(self.split_size_mb.get()) * 1024 * 1024
        except: return
        out_dir = filedialog.askdirectory()
        if not out_dir: return
        curr_content, file_idx = "", 1
        for i, c in enumerate(self.chapters):
            text = self._prepare_content(c)
            if len((curr_content + text).encode('utf-8')) > limit and curr_content:
                name = self._get_filename(file_idx, f"Part{file_idx}")
                with open(os.path.join(out_dir, name), 'w', encoding='utf-8') as f: f.write(curr_content)
                file_idx += 1; curr_content = text
            else: curr_content += text + "\n\n"
        if curr_content:
            name = self._get_filename(file_idx, f"Part{file_idx}")
            with open(os.path.join(out_dir, name), 'w', encoding='utf-8') as f: f.write(curr_content)
        messagebox.showinfo("完成", "按大小分割导出完成")

    def export_by_count(self):
        selected_data = self.get_selected_chapters()
        if not selected_data: return
        try: count_limit = int(self.merge_count.get())
        except: return
        out_dir = filedialog.askdirectory()
        if not out_dir: return
        
        for i in range(0, len(selected_data), count_limit):
            batch = selected_data[i : i + count_limit]
            start_num = batch[0][0] + 1
            end_num = batch[-1][0] + 1
            
            range_title = f"{start_num}~{end_num}章"
            name = self._get_filename(i//count_limit + 1, range_title)
            
            with open(os.path.join(out_dir, name), 'w', encoding='utf-8') as f:
                for _, c in batch: 
                    f.write(self._prepare_content(c) + "\n\n")
        messagebox.showinfo("完成", "批量合并完成")

if __name__ == "__main__":
    # 如果安装了 tkinterdnd2，则使用支持拖拽的 Tk 对象
    if DND_SUPPORT:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    
    TXTSplitter(root)
    root.mainloop()