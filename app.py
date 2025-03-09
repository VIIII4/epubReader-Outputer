from tempfile import TemporaryDirectory
import zipfile
import os
import xml.etree.ElementTree as ET
import urllib.parse
from tempfile import TemporaryDirectory
from tkinter import (
    
    filedialog, 
    ttk, 
    messagebox,  
    BooleanVar,  
    END
)
from tkinterweb import HtmlFrame
import tkinter as tk
from tkinter import filedialog,ttk 
from converter.html2txt import Maindehtml2txt
from converter.txt2html2 import MaindeTxt2Html
from converter.HTML2EPUB.GenerateEpubFramework import MaindeGenerateEpubFramework
from converter.HTML2EPUB.GenerateEPUB import MaindeGenerateEPUB


def ensure_files_exist():
    """
    确保指定的文件路径存在。如果文件不存在，则创建该文件。
    """
    file_paths = [
        r"primary fileSet\txt",r'primary fileSet\epub',r'converter\HTML2EPUB\Interim Warehouse'
    ]
    for file_path in file_paths:
        # 检查文件所在目录是否存在，若不存在则创建
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)


class EpubParser:
    def __init__(self, epub_path):
        self.epub_path = epub_path
        self.temp_dir = TemporaryDirectory()
        self.opf_path = None
        self.spine_items = []
        self.manifest = {}
        self.title = "Untitled"
        
        self.extract_epub()
        self.parse_container()
        self.parse_opf()

    def extract_epub(self):
        with zipfile.ZipFile(self.epub_path, 'r') as zf:
            zf.extractall(self.temp_dir.name)

    def parse_container(self):
        container_path = os.path.join(self.temp_dir.name, 'META-INF', 'container.xml')
        tree = ET.parse(container_path)
        ns = {'ns': 'urn:oasis:names:tc:opendocument:xmlns:container'}
        rootfile = tree.find('.//ns:rootfile', ns)
        if rootfile is not None:
            self.opf_path = os.path.join(self.temp_dir.name, 
                                       urllib.parse.unquote(rootfile.attrib['full-path']))

    def parse_opf(self):
        opf_dir = os.path.dirname(self.opf_path)
        tree = ET.parse(self.opf_path)
        ns = {
            'opf': 'http://www.idpf.org/2007/opf',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }
        
        metadata = tree.find('opf:metadata', ns)
        if metadata is not None:
            title_elem = metadata.find('dc:title', ns)
            if title_elem is not None:
                self.title = title_elem.text
                
        manifest = tree.find('opf:manifest', ns)
        for item in manifest.findall('opf:item', ns):
            item_id = item.attrib['id']
            href = urllib.parse.unquote(item.attrib['href'])
            full_path = os.path.normpath(os.path.join(opf_dir, href))
            self.manifest[item_id] = {
                'path': full_path,
                'type': item.attrib.get('media-type', '')
            }
        
        spine = tree.find('opf:spine', ns)
        for itemref in spine.findall('opf:itemref', ns):
            item_id = itemref.attrib['idref']
            if item_id in self.manifest:
                item = self.manifest[item_id]
                if item['type'] in ['application/xhtml+xml', 'text/html']:
                    self.spine_items.append(item['path'])
                    
                
                
class EnhancedTextEditor:
    def __init__(self, root):
        
        self.root = root
        self.root.title("简单文本编辑器")

        # 创建菜单栏
        self.menu_bar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="新建", command=self.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="打开", command=self.open_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="保存", command=self.save_file, accelerator="Ctrl+S")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="退出", command=self.root.quit, accelerator="Ctrl+Q")
        self.menu_bar.add_cascade(label="文件", menu=self.file_menu)
        self.root.config(menu=self.menu_bar)


        # 创建状态栏
        self.status_label = tk.Label(self.root, text="就绪", anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 绑定快捷键
        self.root.bind_all("<Control-n>", lambda event: self.new_file())
        self.root.bind_all("<Control-o>", lambda event: self.open_file())
        self.root.bind_all("<Control-s>", lambda event: self.save_file())
        self.root.bind_all("<Control-q>", lambda event: self.root.quit())
        
        
        self.root.title("epubManager2")
        self.epub_parser = None
        self.current_epub_dir = None
        self.notebook = None
        self.tree_frame = None
        self.chapter_tree = None
        self.html_frame = None
        
        
        
        self.create_notebook()
        self.create_epub_tab()
        
        self.txtEditer()
        self.update_status()
        self.create_epub_tab
        self.browse_file
        self.browse_dir
        self.create_converter_tab()
        # self.execute_txt2html
        # self.execute_epub2txt
        # self.execute_generate_epub
        # self.execute_create_framework
        
        
        # 修改菜单添加EPUB打开功能
        self.file_menu.insert_command(2, label="打开EPUB", command=self.open_epub)
        
        
    def new_file(self):
        self.text.delete(1.0, tk.END)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text.delete(1.0, tk.END)
                    self.text.insert(tk.END, content)
                self.status_label.config(text=f"文件已打开: {file_path}")
            except Exception as e:
                self.status_label.config(text=f"打开文件时出错: {e}")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                content = self.text.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.status_label.config(text=f"文件已保存到: {file_path}")
            except Exception as e:
                self.status_label.config(text=f"保存文件时出错: {e}")
        
        
    def create_notebook(self):
        """创建Notebook组件"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)   
            
    def txtEditer(self):
        """创建文本编辑页"""
        text_frame = ttk.Frame(self.notebook)
        
        # 创建工具栏
        toolbar = ttk.Frame(text_frame)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # 工具栏按钮
        # new_btn = ttk.Button(toolbar, text="新建", command=self.new_file)
        # open_btn = ttk.Button(toolbar, text="打开", command=self.open_file)
        # save_btn = ttk.Button(toolbar, text="保存", command=self.save_file)
        
        # for btn in [new_btn, open_btn, save_btn]:
        #     btn.pack(side=tk.LEFT, padx=2, pady=2)

        # 文本编辑区域（替换原有直接放在root中的text组件）
        self.text = tk.Text(text_frame, wrap=tk.WORD, undo=True)
        self.text.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(text_frame, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=scrollbar.set)
        
        # 将标签页添加到notebook
        self.notebook.add(text_frame, text="文本编辑")
        
        # 初始化状态
        self.update_status()
        
        
        
    def update_status(self):
        """更新状态栏显示"""
        text = self.text.get("1.0", "end-1c")
        line = self.text.index(tk.INSERT).split('.')[0]
        col = self.text.index(tk.INSERT).split('.')[1]
        self.status_label.config(text=f"行号: {line} 列号: {col} | 字符数: {len(text)}")
        self.text.after(500, self.update_status)  # 实时更新状态
            
        
    def create_converter_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="转换")

        # ==================TXT转HTML区域==================
        txt2html_frame = ttk.LabelFrame(tab, text="文本转HTML")
        txt2html_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        ttk.Button(txt2html_frame, text="选择文本文件", 
                command=lambda: self.browse_file(self.txt_html_input, multiple=True)).grid(row=0, column=0)
        self.txt_html_input = ttk.Entry(txt2html_frame, width=40)
        self.txt_html_input.grid(row=0, column=1, padx=5)
        
        ttk.Button(txt2html_frame, text="输出目录", 
                command=lambda: self.browse_dir(self.txt_html_output)).grid(row=1, column=0)
        self.txt_html_output = ttk.Entry(txt2html_frame, width=40)
        self.txt_html_output.grid(row=1, column=1)
        
        ttk.Button(txt2html_frame, text="开始转换", 
                command=self.execute_txt2html).grid(row=2, columnspan=2, pady=5)

        # ==================EPUB转TXT区域==================
        epub2txt_frame = ttk.LabelFrame(tab, text="EPUB转文本")
        epub2txt_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        self.chapter_var = BooleanVar()
        ttk.Checkbutton(epub2txt_frame, text="转换特定章节", 
                    variable=self.chapter_var).grid(row=0, column=0)
        self.chapter_input = ttk.Entry(epub2txt_frame, width=20)
        self.chapter_input.grid(row=0, column=1, padx=5)
        
        ttk.Button(epub2txt_frame, text="选择EPUB", 
                command=lambda: self.browse_file(self.epub_txt_input)).grid(row=1, column=0)
        self.epub_txt_input = ttk.Entry(epub2txt_frame, width=40)
        self.epub_txt_input.grid(row=1, column=1)
        
        ttk.Button(epub2txt_frame, text="开始转换", 
                command=self.execute_epub2txt).grid(row=2, columnspan=2, pady=5)

        # ==================生成EPUB区域==================
        gen_epub_frame = ttk.LabelFrame(tab, text="生成EPUB")
        gen_epub_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        ttk.Button(gen_epub_frame, text="选择内容目录", 
                command=lambda: self.browse_dir(self.epub_content_dir)).grid(row=0, column=0)
        self.epub_content_dir = ttk.Entry(gen_epub_frame, width=30)
        self.epub_content_dir.grid(row=0, column=1)
        
        ttk.Label(gen_epub_frame, text="输出文件名:").grid(row=1, column=0)
        self.epub_filename = ttk.Entry(gen_epub_frame, width=30)
        self.epub_filename.grid(row=1, column=1)
        
        ttk.Button(gen_epub_frame, text="生成EPUB", 
                command=self.execute_generate_epub).grid(row=2, columnspan=2, pady=5)

        # ==================EPUB框架区域==================
        epub_frame = ttk.LabelFrame(tab, text="EPUB框架模板")
        epub_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

        ttk.Label(epub_frame, text="框架名称:").grid(row=0, column=0)
        self.framework_name = ttk.Entry(epub_frame, width=30)
        self.framework_name.grid(row=0, column=1)
        
        ttk.Button(epub_frame, text="创建框架", 
                command=self.execute_create_framework).grid(row=1, columnspan=2, pady=5)

        # 配置网格布局权重
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        return tab

    # 以下是需要添加到类中的相关方法
    def browse_file(self, entry_widget, multiple=False):
        filetypes = (('Text files', '*.txt'), ('EPUB files', '*.epub'), ('All files', '*.*'))
        if multiple:
            files = filedialog.askopenfilenames(filetypes=filetypes)
            entry_widget.delete(0, END)
            entry_widget.insert(0, ';'.join(files))
        else:
            filename = filedialog.askopenfilename(filetypes=filetypes)
            entry_widget.delete(0, END)
            entry_widget.insert(0, filename)

    def browse_dir(self, entry_widget):
        directory = filedialog.askdirectory()
        entry_widget.delete(0, END)
        entry_widget.insert(0, directory)

    def execute_txt2html(self):
        input_files = self.txt_html_input.get().split(';')
        output_dir = self.txt_html_output.get()
        MaindeTxt2Html(input_files, output_dir)
        messagebox.showinfo("完成", "文本转换HTML已完成！")

    def execute_epub2txt(self):
        input_file = self.epub_txt_input.get()
        judge = self.chapter_var.get()
        cypher = self.chapter_input.get().split(',') if self.chapter_input.get() else []
        Maindehtml2txt(judge, cypher, input_file)
        messagebox.showinfo("完成", "EPUB转换文本已完成！")

    def execute_generate_epub(self):
        content_dir = self.epub_content_dir.get()
        filename = self.epub_filename.get()
        MaindeGenerateEPUB(pointer=content_dir, renamestr=filename)
        messagebox.showinfo("完成", "EPUB生成已完成！")

    def execute_create_framework(self):
        name = self.framework_name.get() or "default_framework"
        MaindeGenerateEpubFramework(renamestr=name)
        messagebox.showinfo("完成", "EPUB框架已创建！")
            
        
        
        
        
    def create_epub_tab(self):
        """创建EPUB阅读页"""
        epub_frame = ttk.Frame(self.notebook)
        
        # 左侧目录树
        self.tree_frame = ttk.Frame(epub_frame, width=200)
        self.tree_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.chapter_tree = ttk.Treeview(self.tree_frame)
        self.chapter_tree.pack(fill=tk.BOTH, expand=True)
        self.chapter_tree.bind("<<TreeviewSelect>>", self.load_selected_chapter)
        
        # 右侧内容显示
        content_frame = ttk.Frame(epub_frame)
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.html_frame = HtmlFrame(content_frame)  
        self.html_frame.pack(fill=tk.BOTH, expand=True)
        
        self.notebook.add(epub_frame, text="EPUB阅读")
        
    def open_epub(self):
        """打开EPUB文件"""
        file_path = filedialog.askopenfilename(filetypes=[("EPUB files", "*.epub")])
        if file_path:
            try:
                self.epub_parser = EpubParser(file_path)
                self.current_epub_dir = self.epub_parser.temp_dir
                self.update_chapter_tree()
                self.status_label.config(text=f"已打开EPUB: {self.epub_parser.title}")
                self.load_chapter(0)  # 默认加载第一个章节
            except Exception as e:
                self.status_label.config(text=f"打开EPUB失败: {e}")
                
    def update_chapter_tree(self):
        """更新目录树"""
        self.chapter_tree.delete(*self.chapter_tree.get_children())
        for idx, path in enumerate(self.epub_parser.spine_items):
            chapter_name = os.path.basename(path)
            self.chapter_tree.insert("", "end", iid=idx, text=(chapter_name.rsplit('.', 1)[0]))
    
    def load_selected_chapter(self, event):
        """加载选中的章节"""
        selected = self.chapter_tree.selection()
        if selected:
            self.load_chapter(int(selected[0]))
            
    def load_chapter(self, index):
        """加载指定章节内容"""
        if not self.epub_parser or index >= len(self.epub_parser.spine_items):
            return
        
        chapter_path = self.epub_parser.spine_items[index]
        try:
            with open(chapter_path, "r", encoding="utf-8") as f:
                content = f.read()
                base_url = f"file://{os.path.dirname(chapter_path)}/"
                self.html_frame.load_html(content, base_url=base_url)
        except Exception as e:
            self.status_label.config(text=f"加载章节失败: {e}")

if __name__ == "__main__":
    ensure_files_exist()
    root = tk.Tk()
    editor = EnhancedTextEditor(root)
    root.mainloop()


