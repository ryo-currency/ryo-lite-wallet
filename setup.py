from cx_Freeze import setup, Executable
from multiprocessing import Queue
import os, sys

base = None
if sys.platform == "win32":
    base = "Win32GUI"

build_exe_options = {"packages": ["os", "idna", "sys"], "excludes": ["tkinter"], "include_files":["Resources/icons/sumokoin.ico"]}
setup( name = "Sumokoin GUI Wallet",
version = "0.0.3",
description = "Sumokoin GUI Wallet for Linux",
options = {"build_exe": build_exe_options},
executables = [Executable("wallet.py", base=base, icon='Resources/icons/sumokoin.ico')])
