import sys,os
from cx_Freeze import setup, Executable
# 添加版本签名（可选）

# 配置参数
base = "Win32GUI" if sys.platform == "win32" else None  # 隐藏控制台窗口（Windows）
include_files = [
    "requirements.txt",                       # 依赖文件
    "README.md",                              # 文档
    r"tupian.ico",
    (os.path.join(sys.base_prefix, "tcl"), "tcl"),  # Python 安装目录的 tcl 文件夹
    (os.path.join(sys.base_prefix, "DLLs", "tk86t.dll"), "tk86t.dll"),  # 根据 Python 版本调整
    (os.path.join(sys.base_prefix, "DLLs", "tcl86t.dll"), "tcl86t.dll")
]
#include_files.append((os.path.join(sys.base_prefix, "tcl"), "tcl"))
setup(
    name="epubOutper",
    version="1.0",
    description="EPUB输出工具",
    options={
        "build_exe": {
            "includes": ["tkinter", "tkinterweb", "bs4", "xml"],  # 强制包含 tkinter 和依赖
            "packages": ["os", "sys", "xml","lxml", "html5lib"],
            "include_files": include_files,
            "path": sys.path + ["./converter/HTML2EPUB"] , # 补充搜索路径
            "excludes": ["pip", "dotenv","cx_Freeze"],  # 排除无关模块
        }
    },
    executables=[
        Executable(
            "app.py",  # 主程序入口
            base=base,
            icon=r"tupian.ico"  # 可选：替换为你的程序图标
        )
    ]
)