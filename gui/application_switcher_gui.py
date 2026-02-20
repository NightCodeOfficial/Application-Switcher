# gui/application_switcher_gui.py
import utils.applications_utils as au
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QFileIconProvider, QLineEdit
from PySide6.QtCore import Qt, QFileInfo, QEvent
from PySide6.QtGui import QKeyEvent
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from pathlib import Path
import os
from PySide6.QtGui import QIcon
from pathlib import Path


_executor = ThreadPoolExecutor(max_workers=1)


def run_function_with_timeout(func, timeout_seconds: float, *args, **kwargs):
    '''
    Runs a function with a timeout.
    '''
    # This will mostly be used to open applications with a timeout to avoid freezing the GUI
    future = _executor.submit(func, *args, **kwargs)
    try:
        future.result(timeout=timeout_seconds)
        return True
    except TimeoutError:
        future.cancel()
        raise TimeoutError(f"Function {func.__name__} timed out after {timeout_seconds} seconds")

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        root = QWidget()
        layout = QVBoxLayout(root)
        self.icon_provider = QFileIconProvider()
        # self._windows_data = au.get_windows_structured_data()
        self._all_windows = list(au.get_windows_structured_data())


        # define widgets
        self.label = QLabel("Application Switcher")
        self.applications_list = QListWidget()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search active applications...")
        self.search_bar.installEventFilter(self)
        self.search_bar.textChanged.connect(self.on_search_bar_text_changed)


        # add widgets to layout
        layout.addWidget(self.search_bar)
        layout.addWidget(self.label)
        layout.addWidget(self.applications_list)
        self.setCentralWidget(root)

        self.setWindowTitle("Application Switcher")
        base_dir = Path(__file__).resolve().parent
        icon_path = base_dir / "icons" / "app_icon.png"
        
        self.setWindowIcon(QIcon(str(icon_path)))
        self.resize(800, 400)
        self.populate_applications_list(self._all_windows)
        self.setStyleSheet(self.load_stylesheet())
        self.applications_list.itemActivated.connect(self.on_activate_list_item)

       
    def eventFilter(self, obj, event):
        if obj is self.search_bar and event.type() == QEvent.KeyPress:
            key = event.key()

            if key in (Qt.Key_Up, Qt.Key_Down, Qt.Key_PageUp, Qt.Key_PageDown):
                # forward navigation keys to the list
                QApplication.sendEvent(self.applications_list, event)
                return True  # we handled it (prevents cursor move in QLineEdit)

            if key in (Qt.Key_Return, Qt.Key_Enter):
                # activate currently selected item
                item = self.applications_list.currentItem()
                if item:
                    self.on_activate_list_item(item)
                return True

        return super().eventFilter(obj, event)

    def initialize_applications_list(self):
        self.applications_list.clear()

        # Populate the list of open applications skipping blank titles and the gui application itself
        for window in self._windows_data:
            title = window['title']
            hwnd = window['hwnd']
            exe = window['exe']
            if "application_switcher_gui.py" in title:
                continue
            # if title == self.windowTitle():
            #     continue
            if title:
                item = QListWidgetItem(title)
                item.setData(Qt.UserRole, hwnd)
                item.setIcon(self.icon_provider.icon(QFileInfo(exe)))
                self.applications_list.addItem(item)
        if self.applications_list.count() > 0:
            self.applications_list.setCurrentRow(0)

    def load_stylesheet(self):
        stylesheet = (Path(__file__).parent / "theme.qss").read_text(encoding="utf-8")
        return stylesheet

    def on_activate_list_item(self, item:QListWidgetItem):
        hwnd = item.data(Qt.UserRole)
        application_opened = run_function_with_timeout(au.open_window, 10, hwnd)
        if application_opened:
            print(f"Activated window: {hwnd}")
        else:
            print(f"Failed to activate window: {hwnd}")

    def on_search_bar_text_changed(self, text:str):
        content = text.strip().lower()

        if not content:
            filtered_items = self._all_windows
        else:
            filtered_items = [
                item for item in self._all_windows 
                if item.get('title') and content in item['title'].lower()
                ]

        self.populate_applications_list(filtered_items)

    def populate_applications_list(self, items:list[dict]):
        self.applications_list.clear()

        # Populate the list of open applications skipping blank titles and the gui application itself
        for window in items:
            title = window.get('title', '')
            hwnd = window.get('hwnd', 0)
            exe = window.get('exe') or ''
            
            if "application_switcher_gui.py" in title:
                continue
            # if title == self.windowTitle():
            #     continue
            if title:
                item = QListWidgetItem(title)
                item.setData(Qt.UserRole, hwnd)
                if exe:
                    item.setIcon(self.icon_provider.icon(QFileInfo(exe)))
                self.applications_list.addItem(item)
        if self.applications_list.count() > 0:
            self.applications_list.setCurrentRow(0)

    



def make_main_window():
    app = QApplication([])
    window = Main()
    window.show()
    app.exec()
    
