import cx_Freeze as cx
import platform, os

include_files = [("abq_data_entry/images", "images")]
base = None
target_name = "abq"

if platform.system() == "Windows":
    PYTHON_DIR = os.path.dirname(os.path.dirname(os.__file__))
    os.environ["TCL_LIBRARY"] = os.path.join(PYTHON_DIR, "tcl", "tcl8.6")
    os.environ["TK_LIBRARY"] = os.path.join(PYTHON_DIR, "tcl", "tk8.6")
    include_files += [
        (os.path.join(PYTHON_DIR, "DLLs", "tcl86t.dll"), ""),
        (os.path.join(PYTHON_DIR, "DLLs", "tk86t.dll"), ""),
    ]
    base = "Win32GUI"
    target_name = "abq.exe"

shortcut_data = [
    (
        "DesktopShortcut",
        "DesktopFolder",
        "ABQ Data Entry",
        "TARGETDIR",
        "[TARGETDIR]" + target_name,
        None,
        "Data Entry application for ABQ Agrilabs",
        None,
        None,
        None,
        None,
        "TARGETDIR",
    ),
    (
        "MenuShortcut",
        "ProgramMenuFolder",
        "ABQ Data Entry",
        "TARGETDIR",
        "[TARGETDIR]" + target_name,
        None,
        "Data Entry application for ABQ Agrilabs",
        None,
        None,
        None,
        None,
        "TARGETDIR",
    ),
]

cx.setup(
    name="ABQ_Data_Entry",
    version="1.0",
    author="Alan D Moore",
    author_email="alandmoore@example.com",
    description="Data entry application for ABQ Agrilabs",
    url="http://abq.example.com",
    packages=["abq_data_entry"],
    executables=[
        cx.Executable(
            "abq_data_entry.py", base=base, targetName=target_name, icon="abq.ico"
        )
    ],
    options={
        "build_exe": {
            "packages": ["psycopg2", "requests", "matplotlib", "numpy"],
            "includes": ["idna.idnadata", "zlib"],
            "include_files": include_files,
            "excludes": [
                "PyQt4",
                "PyQt5",
                "PySide",
                "IPython",
                "jupyter_client",
                "jupyter_core",
                "ipykernel",
                "ipython_genutils",
                "black",
                "test",
                "unittest",
                "pandas",
                "openpyxl",
                "jedi",
                "matplotlib_inline",
                "pytz",
            ],
        },
        "bdist_msi": {
            "upgrade_code": "{F5607105-8CB6-463C-84FA-FC163B562EFF}",
            "data": {"Shortcut": shortcut_data},
        },
    },
)
