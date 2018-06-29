import sys
from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="代码统计器",
      version="0.1",
      description="统计代码行数",
      options={"build_exe": build_exe_options},
      executables=[Executable("CodeCount.py", base=base, targetName="代码统计器.exe")])  # targetName 是生成的 exe 文件名
