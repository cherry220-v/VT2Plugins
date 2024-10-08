from PyQt5.QtCore import QProcess, pyqtSignal, pyqtSlot, QThread
from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QApplication

class ProcessOutputReader(QProcess):
    produce_output = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.readyReadStandardOutput.connect(self._ready_read_standard_output)

    @pyqtSlot()
    def _ready_read_standard_output(self):
        raw_bytes = self.readAllStandardOutput()
        text = raw_bytes.data().decode('utf-8')
        self.produce_output.emit(text)

class MyConsole(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setReadOnly(True)
        self.setMaximumBlockCount(10000)

    @pyqtSlot(str)
    def append_output(self, text):
        self.append(text)

class ProcessThread(QThread):
    output_ready = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.reader = ProcessOutputReader()

    def run(self):
        self.reader.produce_output.connect(self.output_ready.emit)
        self.reader.start('python3', ['-u', self.file_path])
        self.reader.waitForFinished()  # Wait for the process to finish

class ProcessManager:
    def __init__(self):
        self.process_threads = []

    def run_file(self, file_path):
        thread = ProcessThread(file_path)
        console = MyConsole()

        # Подключаем сигнал вывода к консоли
        thread.output_ready.connect(console.append_output)

        # Запускаем поток
        thread.start()

        # Показать консоль в отдельном окне
        console_widget = QWidget()
        layout = QVBoxLayout(console_widget)
        layout.addWidget(console)
        console_widget.setWindowTitle("Process Output")
        console_widget.resize(600, 400)
        console_widget.show()

# Основной код приложения
app = QApplication([])

# Создаем экземпляр ProcessManager
process_manager = ProcessManager()

def runFile():
    tab = vtapi.Tab.currentTabIndex()
    if vtapi.Tab.getTabFile(tab):
        process_manager.run_file(vtapi.Tab.getTabFile(tab))

# Запускаем основной цикл приложения
app.exec_()
