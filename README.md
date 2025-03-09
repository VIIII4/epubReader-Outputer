# EPUB 文档管理工具

## 项目简介
本工具提供 EPUB 文档的全生命周期管理，支持格式转换、内容编辑、元数据修改等功能，基于 `tkinter` 实现图形化界面。当前版本支持 Windows 系统。

---

## 主要功能

### 转换工具
1. **EPUB → TXT 转换**  
   - 支持选择性转换特定章节（通过界面勾选）
   - 自动处理章节标题与内容分割

2. **TXT → HTML 转换**  
   - 生成符合 EPUB 标准的 XHTML 格式
   - 自动识别列表项（`•`开头）并转换为 `<ul>` 列表

3. **HTML → EPUB 框架生成**  
   - 创建标准 EPUB 目录结构（含 `META-INF`, `OEBPS`）
   - 自动生成封面页、导航目录（`nav.xhtml`）和样式表（`style.css`）

### EPUB 管理
- **创建 EPUB 模板**：快速初始化包含基础结构的 EPUB 框架
- **动态编辑章节**：通过文本编辑器实时修改章节内容后更新 EPUB
- **元数据修改**：支持编辑标题、作者等信息
- **预览功能**：内置 HTML 预览窗口（依赖 `tkinterweb`）
- **章节管理**：删除指定章节或封面图片

---

## 环境要求
```bash
# 安装依赖库
pip install -r requirements.txt

# requirements.txt 内容：
tkinterweb
beautifulsoup4




使用说明
快速开始
启动程序

bash
python app.py
功能操作示例

TXT 转 HTML：

在「转换」标签页选择文本文件
指定输出目录后点击「开始转换」
生成的 XHTML 文件将用于后续 EPUB 组装
生成 EPUB：

完成 HTML 文件准备后，通过「EPUB 管理」标签创建框架
在弹出界面输入书名、作者并指定封面图片
点击「生成 EPUB」完成打包
元数据编辑
打开现有 EPUB 后，在「元数据」输入框修改标题/作者，保存后自动生成新版本文件。

注意事项
依赖库说明

tkinterweb：用于 HTML 内容预览
beautifulsoup4：处理 HTML 内容解析（如 EPUB 转 TXT）
文件格式要求

TXT 文件章节需按 === 标题 === 格式分隔，否则以文件名作为标题
当前限制

仅支持 Windows 系统（依赖 tkinter 的某些特性）
图片处理功能待完善（如封面需手动放置到指定目录）
后续优化计划
 实现后台守护进程（daemon 模式）
 添加 REST API 接口支持
 多线程加速文件转换与打包流程
 增加图片压缩功能（依赖 Pillow 库）


项目根目录
├── app.py               # 主程序入口
├── converter/           # 核心转换模块
│   ├── html2txt.py      # EPUB→TXT 转换
│   ├── txt2html2.py     # TXT→HTML 转换
│   └── HTML2EPUB/       # EPUB 生成相关
│       ├── GenerateEPUB.py
│       └── GenerateEpubFramework.py
└── README.md            # 本文档

### 打包
python setup.py build  # 生成打包文件（输出到 build 目录）
python setup.py bdist_msi  # 生成 Windows 安装包（.msi）
