from PyQt5.uic.Compiler.qtproxies import QtGui, QtWidgets
from PyQt6 import QtCore, QtWidgets
import sys, os, subprocess

import threading
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import *


pathFile = open("pythonpath", "a+")

class CustomDialog(QtWidgets.QDialog):
    def __init__(self, vtapi):
        super().__init__()
        self.vtapi = vtapi
        self.platform = self.vtapi.FSys.platformModule()
        self.os = self.vtapi.FSys.osModule()
        self.platform = self.vtapi.FSys.platformModule()
        self.subprocess = self.vtapi.FSys.sprModule()
        self.setupUi()
    def setupUi(self):
        self.setObjectName("self")
        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.resize(400, 111)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMaximumSize(QtCore.QSize(400, 111))
        self.setWindowFilePath("")
        self.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(parent=self)
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(parent=self.frame)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit = QtWidgets.QLineEdit(parent=self.frame)
        self.lineEdit.setObjectName("comboBox")
        self.lineEdit.insert(pathFile.read().split("\n")[0] if self.os.path.isfile(pathFile.read().split("\n")[0]) else self.findPython()[0])
        self.horizontalLayout.addWidget(self.lineEdit)
        self.pushButton = QtWidgets.QPushButton(parent=self.frame)
        self.pushButton.setMaximumSize(QtCore.QSize(50, 16777215))
        self.pushButton.clicked.connect(self.customPythonPath)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.frame)
        self.pushButton_2.clicked.connect(self.savePath)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout_2.addWidget(self.pushButton_2)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("self", "Choose Python path - "))
        self.label.setText(_translate("self", "Choose Python path"))
        self.pushButton.setText(_translate("self", "Add"))
        self.pushButton_2.setText(_translate("self", "Save"))

    def customPythonPath(self):
        path = self.vtapi.App.openFileDialog()
        if path[0]:
            self.lineEdit.clear()
            self.lineEdit.insert(path[0][0])

    def savePath(self):
        t = self.lineEdit.text()
        if t:
            pathFile.write(t)
        self.close()

    def findPython(self):
        system_type = self.platform.system()

        if system_type == "Windows":
            return self.find_python_windows()
        elif system_type in ("Linux", "Darwin"):  # macOS == Darwin
            return self.find_python_unix()
        else:
            return "", ""

    def find_python_windows(self):
        paths = self.os.environ["PATH"].split(self.os.pathsep)
        for path in paths:
            python_exe = self.os.path.join(path, "python.exe")
            if self.os.path.exists(python_exe):
                try:
                    version = self.subprocess.check_output([python_exe, "--version"],
                                                      stderr=self.subprocess.STDOUT).decode().strip()
                    return python_exe, version
                except self.subprocess.SubprocessError:
                    continue
        return "", ""

    def find_python_unix(self):
        try:
            python_path = self.subprocess.check_output(["which", "python3"]).decode().strip()
            if python_path:
                version = self.subprocess.check_output([python_path, "--version"]).decode().strip()
                return python_path, version
        except self.subprocess.CalledProcessError:
            pass

        try:
            python_path = self.subprocess.check_output(["which", "python"]).decode().strip()
            if python_path:
                version = self.subprocess.check_output([python_path, "--version"]).decode().strip()
                return python_path, version
        except self.subprocess.CalledProcessError:
            pass

        return "", ""

class Worker(QObject):
    output_ready = pyqtSignal(str)

    def run_script(self, file_path):
        command = [sys.executable, file_path]

        try:
            # Запускаем процесс
            result = subprocess.run(command, capture_output=True, text=True)

            # Выводим результат в сигнал
            self.output_ready.emit(result.stdout)
            if result.stderr:
                self.output_ready.emit(f"Ошибка:\n{result.stderr}")

        except Exception as e:
            self.output_ready.emit(f"Ошибка при выполнении: {str(e)}")


class PythonRunner(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Python Console")

        layout = QVBoxLayout()

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        self.setLayout(layout)

        self.worker = Worker()
        self.worker.output_ready.connect(self.update_output)

    def runFile(self, f):
        threading.Thread(target=self.worker.run_script, args=(f,), daemon=True).start()

    def update_output(self, text):
        self.output_area.append(text)
