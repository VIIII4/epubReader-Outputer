import os
import zipfile
import xml.etree.ElementTree as ET
from lxml import etree


import re
def remove_ampersand_in_xml_file(file_path):
    """
    此函数用于清除 XML 文件中的 & 字符
    :param file_path: XML 文件的路径
    :return: 无，直接修改并保存文件
    """
    try:
        parser = etree.XMLParser(encoding='utf-8', recover=True)  # 支持错误恢复
        tree = etree.parse(file_path, parser=parser)
        root = tree.getroot()

        # 遍历 XML 树中的所有元素
        for elem in root.iter():
            if elem.text is not None:
                # 处理元素的文本内容
                elem.text = elem.text.replace('&', '')
            if elem.tail is not None:
                # 处理元素的尾部文本
                elem.tail = elem.tail.replace('&', '')

        # 保存修改后的 XML 文件
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
        print("XML 文件中的 & 字符已清除。")
        return True
    except ET.ParseError as e:
        print(f"解析 XML 文件时出错: {e}")
    except Exception as e:
        print(f"处理文件时发生其他错误: {e}")





def update_nav_xhtml(input_path, chapters):
    # 在update_nav_xhtml函数中添加调试信息
    
    nav_path = os.path.join(input_path, 'OEBPS', 'nav.xhtml')
    namespaces = {
        'xhtml': 'http://www.w3.org/1999/xhtml',
        'epub': 'http://www.idpf.org/2007/ops'
    }
    
    # 解析现有导航文件
    tree = ET.parse(nav_path)
    root = tree.getroot()
    
    # 查找目录列表
    ol_element = root.find('.//xhtml:nav[@epub:type="toc"]//xhtml:ol', namespaces)
    if ol_element is None:
        raise ValueError("导航文件中找不到目录列表结构")
    
    # 清空现有目录项
    for child in list(ol_element):
        ol_element.remove(child)
    
    # 添加新目录项
    for idx, chap_path in enumerate(chapters, 1):
        try:
            # 提取章节信息
            print(f"Parsing chapter: {chap_path}")  # 添加在for循环内
            chap_filename = os.path.basename(chap_path)
            
           
            parser = etree.XMLParser(encoding='utf-8')  # 增加错误恢复
            chap_tree = etree.parse(chap_path, parser=parser)
            chap_root = chap_tree.getroot()
            h1_element = chap_root.find('.//{*}h1')
            title = h1_element.text if h1_element is not None else f"章节 {idx}"
            
        except Exception as e:
            print(f"Error parsing chapter {chap_path}: {e}")  # 添加在except块内     
            if remove_ampersand_in_xml_file(f'{chap_path}') is True:
                print(f"Parsing chapter: {chap_path}")  # 添加在for循环内
                chap_filename = os.path.basename(chap_path)
                
            
                parser = etree.XMLParser(encoding='utf-8')  # 增加错误恢复
                chap_tree = etree.parse(chap_path, parser=parser)
                chap_root = chap_tree.getroot()
                h1_element = chap_root.find('.//{*}h1')
                title = h1_element.text if h1_element is not None else f"章节 {idx}"
            continue
        
        
        # 创建列表项
        li = ET.Element('{http://www.w3.org/1999/xhtml}li')
        a = ET.SubElement(li, '{http://www.w3.org/1999/xhtml}a', {
            'href': f'text/{chap_filename}'
        })
        a.text = title
        
        ol_element.append(li)
    
    # 保持XML声明和格式
    tree.write(nav_path, 
              encoding='utf-8', 
              xml_declaration=True, 
              method='xml', 
              short_empty_elements=False)

def folder_to_epub(input_path, output_epub_path):
    # 确保输入路径存在
    if not os.path.isdir(input_path):
        raise ValueError("输入路径不存在或不是目录")

    # 收集章节文件
    text_dir = os.path.join(input_path, 'OEBPS', 'text')
    chapters = []
    for root, dirs, files in os.walk(text_dir):
        for file in files:
            if file.endswith('.xhtml'):
                chapters.append(os.path.join(root, file))
    # 按文件名排序
    chapters.sort()

    # 处理OPF文件
    opf_path = os.path.join(input_path, 'OEBPS', 'package.opf')
    namespaces = {
        'opf': 'http://www.idpf.org/2007/opf',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }
    ET.register_namespace('opf', namespaces['opf'])
    ET.register_namespace('dc', namespaces['dc'])
    tree = ET.parse(opf_path)
    root = tree.getroot()

    # 更新manifest
    manifest = root.find('opf:manifest', namespaces)
    # 删除旧的章节条目
    for item in list(manifest):
        href = item.get('href', '')
        if href.startswith('text/') and href.endswith('.xhtml'):
            manifest.remove(item)
    # 添加新章节到manifest
    for chap_path in chapters:
        rel_path = os.path.relpath(chap_path, os.path.dirname(opf_path))
        rel_path = rel_path.replace(os.path.sep, '/')
        item_id = os.path.splitext(os.path.basename(chap_path))[0]
        item = ET.SubElement(manifest, '{http://www.idpf.org/2007/opf}item', {
            'id': item_id,
            'href': rel_path,
            'media-type': 'application/xhtml+xml'
        })

    # 更新spine
    spine = root.find('opf:spine', namespaces)
    # 清空原有spine
    for itemref in list(spine):
        spine.remove(itemref)
    # 添加新章节到spine
    for chap_path in chapters:
        item_id = os.path.splitext(os.path.basename(chap_path))[0]
        ET.SubElement(spine, '{http://www.idpf.org/2007/opf}itemref', {
            'idref': item_id
        })

    # 保存修改后的OPF文件
    tree.write(opf_path, encoding='utf-8', xml_declaration=True)

    # 处理导航文件nav.xhtml
    update_nav_xhtml(input_path, chapters)

    # 打包为EPUB文件
    with zipfile.ZipFile(output_epub_path, 'w') as zipf:
        # 首先添加mimetype（必须无压缩）
        mimetype_path = os.path.join(input_path, 'mimetype')
        zipf.write(mimetype_path, 'mimetype', compress_type=zipfile.ZIP_STORED)
        
        # 添加其他文件
        for root_dir, _, files in os.walk(input_path):
            for file in files:
                file_path = os.path.join(root_dir, file)
                if file == 'mimetype':
                    continue  # 已单独处理
                # 计算相对路径
                arcname = os.path.relpath(file_path, input_path)
                arcname = arcname.replace(os.path.sep, '/')
                # 写入ZIP
                zipf.write(file_path, arcname)

def has_file_extension(file_name):
    parts = file_name.rsplit('.', 1)
    return len(parts) > 1


def MaindeGenerateEPUB(pointer=None,renamestr=None):
    basepath2 = os.path.join('primary fileSet','epub')
    if not os.path.exists(basepath2):
        os.makedirs(basepath2)
    # if renamestr == "" or renamestr is None:
    #     renamestr = "example.epub"
    
    if has_file_extension(renamestr) == False:
        renamestr += ".epub"
    
    
    # elif endwith(renamestr) == False:
    #     renamestr = renamestr + ".epub"

    # if pointer == "" or pointer is None:
    #     pointer = "第一个"
    epub_path = os.path.join('converter', 'HTML2EPUB', 'Interim Warehouse', str(pointer))
    folder_to_epub(epub_path,renamestr)



if __name__ == '__main__':
    # 示例用法
    MaindeGenerateEPUB(pointer='第一个',renamestr='ex.epub')