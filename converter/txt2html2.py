import os
import re

class Txt2Html:
    def __init__(self, input_file, output_dir,filename):
        self.input_file = input_file
        self.output_dir = output_dir
        self.filename = filename
        os.makedirs(output_dir, exist_ok=True)

    def parse(self):
        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = self._split_sections(content)
        for title, body in sections:
            html_content = self._generate_html(title, body)
            self._write_file(title, html_content)

    def _split_sections(self, content):
        pattern = r'^=== (.*?) ===$'
        sections = []
        current_title = None
        current_body = []
        
        for line in content.splitlines():
            match = re.match(pattern, line)
            if match:
                if current_title is not None:
                    sections.append((current_title, current_body))
                current_title = match.group(1)
                current_body = []
            else:
                current_body.append(line)
        
        if current_title is not None:
            sections.append((current_title, current_body))
    
        if not sections:
            title = os.path.splitext(os.path.basename(self.filename))[0]
            return [(title, content.splitlines())]
        return sections

    def _generate_html(self, title, body):
        filtered = [line.rstrip('\n') for line in body]
        processed = filtered[1:] if filtered else []
        
        elements = []
        in_list = False
        paragraph = []
        current_paragraph = ""    
        for line in processed:
            if line.startswith('•'):
                if paragraph:
                    elements.append(f'<p>{"".join(paragraph)}</p>')
                    paragraph = []
                if not in_list:
                    elements.append('<ul>')
                    in_list = True
                elements.append(f'    <li>{line[1:].strip()}</li>')
                
            else:
                if in_list:
                    elements.append('</ul>')
                    in_list = False
                
                # 每行文本单独生成段落
                if line:
                    elements.append(f'<p>{line}</p>')
                elif line == '':
                    elements.append(f'<p></p>')
        



        if in_list:
            elements.append('</ul>')
        if paragraph:
            elements.append(f'<p>{"".join(paragraph)}</p>')
        
        return f'''<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{title}</title>
<link rel="stylesheet" href="../styles/style.css"/></head>
<body>
    <section class="chapter">
        <h1>{title}</h1>
        {"        ".join(elements)}
    </section>
</body>
</html>'''

    def _write_file(self, title, content):
        filename = f"{title.replace(' ', '_')}.xhtml"
        path = os.path.join(self.output_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

def MaindeTxt2Html(input_file, output_file):
    if type(input_file) == list:
        input_files = input_file

        for file_path in input_files:
            inp = os.path.join('primary fileSet','txt',str(file_path))
            o = os.path.join('converter','HTML2EPUB','Interim Warehouse',str(output_file),'OEBPS','text')
            converter = Txt2Html(inp,o,str(file_path))
            converter.parse()
    else:
        inp = os.path.join('primary fileSet','txt',str(input_file))
        o = os.path.join('converter','HTML2EPUB','Interim Warehouse',str(output_file),'OEBPS','text')
        converter = Txt2Html(inp,o,str(input_file))
        converter.parse()


# 使用示例
if __name__ == "__main__":
    #MaindeTxt2Html("某库中的类.txt", "第一个")
    def get_file_list(folder_path):
        """
        该函数用于打开指定文件夹，遍历其中所有文件，并返回文件名列表。
        :param folder_path: 要遍历的文件夹路径
        :return: 包含所有文件名的列表
        """
        file_list = []
        # 检查文件夹路径是否存在
        if os.path.exists(folder_path):
            # 遍历文件夹及其子文件夹
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    # 构建文件的完整路径
                    file_path = os.path.join(root, file)
                    # 将文件名添加到列表中
                    file_list.append(file)
        return file_list

    MaindeTxt2Html(get_file_list('primary fileSet/txt'), "第一个")