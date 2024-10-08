import sys

from PyQt5.uic.Compiler.qtproxies import QtCore
from PyQt6.QtCore import QProcess, QObject
from pexpect.replwrap import python

pyFile = open("pythonpath", "a+")

def pythonPath():
    return pyFile.read().split("\n")[0]

def initAPI(api):
    global vtapi, platform, os, CustomDialog
    vtapi = api
    m = vtapi.FSys
    os = m.osModule()
    from dialogClass import CustomDialog

def runFile():
    tab = vtapi.Tab.currentTabIndex()
    process = QProcess()

    script_path = vtapi.Tab.getTabFile(tab)
    sys.path.insert(0, pythonPath())

    if os.name == 'nt':  # Если Windows
        cmd_command = f"start cmd.exe /k python {script_path} & timeout /t -1"
        process.start("cmd.exe", ["/c", cmd_command])
    else:  # Если Linux или другие ОС
        bash_command = f"bash -c \"python3 {script_path}; read -p 'Press Enter to continue...'\""
        process.start("x-terminal-emulator", ["-e", bash_command])

    process.waitForFinished()

def showPythonPath():
    d = CustomDialog(vtapi)
    d.exec()