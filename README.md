# 如何安装？
- 1. 添加路径。

需要开启 USV 时，需要将 `bin/` 文件夹里的东西拷贝到Windows 搜索路径下（推荐 `C:\Windows\System32`）

- 2. 编译项目。

使用 `Python3.10` 。如下，安装依赖包。
```bash
pip install -r requirements.txt
```

打包成exe文件
```bash
pyinstaller.exe --noconsole f2_sync.py -i F2.ico --add-data "./*.ico;." --hidden-import win32api --hidden-import  pythonwin --hidden-import win32com --hidden-import win32comext --hidden-import isapi
```