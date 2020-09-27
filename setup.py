import sys
from cx_Freeze import setup, Executable

base = 'Win32GUI' if sys.platform == 'win32' else None

bdist_msi_options = {
    'add_to_path': False,
    }
    
build_exe_options = dict(
    packages = ["os", "sys","math","PySide2.QtCore","Pyside2.QtWidgets","PySide2.QtGui"], excludes = []
)

setup(name = "Calculator",
      version = "0.1",
      description = "Demo app",
      executables = [Executable("main.py", base=base)],
      options={'bdist_msi': bdist_msi_options,'build_exe': build_exe_options})