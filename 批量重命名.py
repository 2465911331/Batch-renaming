import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import logging
from PIL import Image

# 初始化日志记录
logging.basicConfig(
    filename="rename_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8-sig"
)

class BatchRenamerApp:
    def __init__(self, master):
        self.master = master
        master.title("批量文件重命名工具")
        master.minsize(600, 450)

        # --- Variables ---
        self.target_directory = tk.StringVar()
        self.name_pattern = tk.StringVar(value="Item_{num}{ext}")
        self.start_number = tk.StringVar(value="1")
        self.num_digits = tk.StringVar(value="3")
        self.file_filter = tk.StringVar(value="*.jpg;*.png;*.gif;*.txt;*.pdf;*.docx;*.xlsx;*.mp4;*.mp3")
        self.rename_plan = []
        self.include_all_files = tk.BooleanVar(value=False)

        # --- GUI Layout ---
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.master, text="目标文件夹:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(self.master, textvariable=self.target_directory, width=50).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(self.master, text="浏览...", command=self.browse_directory).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(self.master, text="命名格式:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(self.master, textvariable=self.name_pattern, width=50).grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(self.master, text="使用 {num}, {ext}, {orig_name}").grid(row=2, column=1, columnspan=2, padx=5, pady=0, sticky=tk.W)

        num_frame = ttk.LabelFrame(self.master, text="编号选项", padding=(10, 5))
        num_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(num_frame, text="起始编号:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(num_frame, textvariable=self.start_number, width=7).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(num_frame, text="编号位数:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(num_frame, textvariable=self.num_digits, width=7).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        ttk.Label(num_frame, text="文件过滤器:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(num_frame, textvariable=self.file_filter, width=20).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(num_frame, text="(例如: *.jpg;*.png;*.gif)").grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky=tk.W)

        ttk.Checkbutton(num_frame, text="包含所有文件类型", variable=self.include_all_files).grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky=tk.W)

        action_frame = ttk.Frame(self.master, padding=(0, 10))
        action_frame.grid(row=4, column=0, columnspan=3, pady=5)
        ttk.Button(action_frame, text="生成预览", command=self.update_preview).pack(side=tk.LEFT, padx=10)
        self.rename_button = ttk.Button(action_frame, text="执行重命名", command=self.perform_rename, state=tk.DISABLED)
        self.rename_button.pack(side=tk.LEFT, padx=10)

        ttk.Label(self.master, text="预览 (旧文件名 -> 新文件名):").grid(row=5, column=0, padx=5, pady=2, sticky=tk.NW)
        self.preview_text = scrolledtext.ScrolledText(self.master, height=15, width=70, wrap=tk.NONE)
        self.preview_text.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky=tk.NSEW)
        self.preview_text.config(state=tk.DISABLED)

        self.status_var = tk.StringVar(value="请选择文件夹并配置参数。")
        ttk.Label(self.master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).grid(row=7, column=0, columnspan=3, padx=0, pady=2, sticky=tk.EW)

        # 文件列表框
        ttk.Label(self.master, text="文件列表:").grid(row=5, column=0, padx=5, pady=2, sticky=tk.W)
        self.file_listbox = tk.Listbox(self.master, selectmode=tk.EXTENDED, height=10)
        self.file_listbox.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)

        # 排序按钮
        sort_frame = ttk.Frame(self.master)
        sort_frame.grid(row=6, column=2, padx=5, pady=5, sticky=tk.N)
        ttk.Button(sort_frame, text="上移", command=self.move_up).pack(fill=tk.X, pady=2)
        ttk.Button(sort_frame, text="下移", command=self.move_down).pack(fill=tk.X, pady=2)
        ttk.Button(sort_frame, text="清空列表", command=self.clear_file_list).pack(fill=tk.X, pady=2)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.target_directory.set(directory)
            self.status_var.set(f"已选择文件夹: {directory}")
            self.clear_preview()

            # 加载文件到列表框
            self.file_listbox.delete(0, tk.END)
            file_filter = self.file_filter.get()
            filters = [ext.strip('*') for ext in file_filter.split(';')] if not self.include_all_files.get() else None
            files = [
                f for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f)) and (filters is None or any(f.endswith(ext) for ext in filters))
            ]
            for file in files:
                self.file_listbox.insert(tk.END, file)

    def clear_preview(self):
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete('1.0', tk.END)
        self.preview_text.config(state=tk.DISABLED)
        self.rename_button.config(state=tk.DISABLED)
        self.rename_plan = []

    def update_preview(self):
        self.clear_preview()
        directory = self.target_directory.get()
        pattern = self.name_pattern.get()

        if not directory or not os.path.isdir(directory):
            messagebox.showerror("错误", "请选择有效的文件夹。")
            return
        if '{num}' not in pattern or '{ext}' not in pattern:
            messagebox.showerror("错误", "命名格式必须包含 {num} 和 {ext}。")
            return

        try:
            start_num = int(self.start_number.get())
            digits = int(self.num_digits.get())
        except ValueError:
            messagebox.showerror("错误", "起始编号和编号位数必须是整数。")
            return

        # 获取文件列表
        files = list(self.file_listbox.get(0, tk.END))
        if not files:
            messagebox.showinfo("信息", "文件列表为空，请先加载文件。")
            return

        self.rename_plan = []
        preview_content = []
        for i, filename in enumerate(files, start=start_num):
            original_name, ext = os.path.splitext(filename)
            try:
                new_name = pattern.format(num=str(i).zfill(digits), ext=ext, orig_name=original_name)
            except KeyError as e:
                messagebox.showerror("错误", f"命名格式错误: 缺少 {e} 占位符。")
                return
            self.rename_plan.append((filename, new_name))
            preview_content.append(f"{filename} -> {new_name}\n")

        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.insert(tk.END, ''.join(preview_content))
        self.preview_text.config(state=tk.DISABLED)
        self.rename_button.config(state=tk.NORMAL)
        self.status_var.set(f"预览完成，共 {len(self.rename_plan)} 个文件。")

    def perform_rename(self):
        directory = self.target_directory.get()
        if not self.rename_plan:
            messagebox.showinfo("信息", "没有可执行的重命名操作。")
            return

        for old_name, new_name in self.rename_plan:
            old_path = os.path.join(directory, old_name)
            new_path = os.path.join(directory, new_name)
            if os.path.exists(new_path):
                logging.warning(f"目标文件已存在，跳过: {new_name}")
                continue
            try:
                os.rename(old_path, new_path)
                logging.info(f"成功: {old_name} -> {new_name}")
            except Exception as e:
                logging.error(f"失败: {old_name} -> {new_name}: {e}")

        messagebox.showinfo("完成", "重命名操作已完成。")
        self.clear_preview()

    def move_up(self):
        selected = self.file_listbox.curselection()
        if not selected:
            return
        for index in selected:
            if index > 0:
                file = self.file_listbox.get(index)
                self.file_listbox.delete(index)
                self.file_listbox.insert(index - 1, file)
                self.file_listbox.select_set(index - 1)

    def move_down(self):
        selected = self.file_listbox.curselection()
        if not selected:
            return
        for index in reversed(selected):
            if index < self.file_listbox.size() - 1:
                file = self.file_listbox.get(index)
                self.file_listbox.delete(index)
                self.file_listbox.insert(index + 1, file)
                self.file_listbox.select_set(index + 1)

    def clear_file_list(self):
        self.file_listbox.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchRenamerApp(root)
    root.mainloop()