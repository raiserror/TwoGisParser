from cx_Freeze import setup, Executable
import sys

build_exe_options = {
    "packages": ["tkinter", "sv_ttk", "pytest-playwright", "googletrans", 'openpyxl'],
    "include_files": [],
    "excludes": ["test"],
    "include_msvcr": True,
    "optimize": 2,
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Парсер 2GIS",
    version="2.0",
    description="Парсер 2GIS",
    options={"build_exe": build_exe_options},
    executables=[Executable("gui.py", 
                          base=base, 
                          icon="static/mappin.png",
                          target_name="TwoGisParser.exe")]
)