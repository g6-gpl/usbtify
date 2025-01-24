import os
import shutil
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QWidget,
    QListWidget,
    QProgressBar,
    QDialog,
    QFormLayout,
    QMenuBar,
    QAction,
    QMenu,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
)
from PyQt5.QtCore import QThread, pyqtSignal
import win32api
import win32file
import win32con


class DatabaseManager:
    DB_NAME = "usb_log.db"

    # def __init__(self, source_file, dest_path):
    #     super().__init__()
    #     self.source_file = source_file
    #     self.dest_path = dest_path

    def __init__(self):
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT,
                file_name TEXT,
                file_size INTEGER,
                usb_serial TEXT,
                usb_path TEXT,
                timestamp TEXT
            )
        """
        )
        cursor.execute(
            """
                    CREATE TABLE IF NOT EXISTS folderPath (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        folder_path TEXT,
                        timestamp TEXT
                        )
                    """
        )
        cursor.execute(
            """
                    CREATE TABLE IF NOT EXISTS sourceFilePath (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_file_path TEXT,
                        timestamp TEXT
                        )
                    """
        )
        cursor.execute(
            """
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_name TEXT,
                        timestamp TEXT
                        )
                    """
        )
        conn.commit()
        conn.close()

    def get_drive_serial_number(self, drive_letter: str) -> str:
        try:
            volume_info = win32api.GetVolumeInformation(drive_letter)
            serial_number = volume_info[1]
            return f"{serial_number:08X}"
        except Exception as e:
            return f"{e}"

    def save_log(self, user_name, file_name, file_size, usb_path):
        try:
            usb_serial = self.get_drive_serial_number(usb_path)
            conn = sqlite3.connect(self.DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO logs (user_name, file_name, file_size, usb_serial, usb_path, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    user_name,
                    file_name,
                    file_size,
                    usb_serial,
                    usb_path,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            conn.commit()
        except Exception as e:
            print(f"Ошибка при сохранении лога: {e}")
        finally:
            conn.close()

    def save_source_folder_path(self, folder_path):
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO folderPath(folder_path, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """,
            (folder_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        conn.close()

    def save_source_folder_path(self, source_file_path):
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO sourceFilePath(source_file_path, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """,
            (source_file_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        conn.close()

    def load_users(self):
        conn = sqlite3.connect("usb_log.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_name from users")
        rows = cursor.fetchall()
        
        self.user_table.setRowCount(len(rows))
        for i,row, in enumerate(rows):
            for j, item, in enumerate(row):
                self.user_table.setItem(i,j, QTableWidgetItem(str(item)))
                
        conn.close()
        
    def add_user(self, user_name):
        self.cursor.execute("INSERT INTO users (user_name) VALUES (?)", (user_name,))
        self.conn.commit()
    
    def update_user(self, user_id, new_name):
        pass

    def delete_user(self, user_id):
        pass
    
    def close(self):
        self.conn.close()


class FileCopyThread(QThread):
    progress = pyqtSignal(int)  # Сигнал для обновления прогресс-бара
    finished = pyqtSignal(str)  # Сигнал для завершения копирования

    def __init__(self, source_file, dest_path):
        super().__init__()
        self.source_file = source_file
        self.dest_path = dest_path

    def run(self):
        try:
            total_size = os.path.getsize(self.source_file)
            copied_size = 0

            os.makedirs(os.path.dirname(self.dest_path), exist_ok=True)
            with open(self.source_file, "rb") as src, open(self.dest_path, "wb") as dst:
                while chunk := src.read(1024 * 1024):  # Копируем по 1 МБ
                    dst.write(chunk)
                    copied_size += len(chunk)
                    progress = int((copied_size / total_size) * 100)
                    self.progress.emit(progress)  # Обновляем прогресс-бар
            self.finished.emit("Файл успешно загружен!")
        except Exception as e:
            self.finished.emit(f"Ошибка: {str(e)}")


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")

        self.setGeometry(300, 300, 300, 200)

        layout = QFormLayout()
        self.default_folder_input = QLineEdit(self)
        self.default_folder_input.setText("UploadedFiles")
        layout.addRow("Папка загрузки:", self.default_folder_input)

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_settings(self):
        folder = self.default_folder_input.text()
        self.accept()


class StatisticsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Статистика")
        self.setGeometry(100, 100, 900, 400)

        layout = QVBoxLayout()
        self.table = QTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            [
                "Имя пользователя",
                "Имя файла",
                "Размер файла",
                "USB-носитель",
                "Название тома",
                "Время",
            ]
        )

        layout.addWidget(self.table)

        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        conn = sqlite3.connect("usb_log.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM logs")

        rows = cursor.fetchall()
        print(rows)
        self.table.setRowCount(len(rows))
        for (
            i,
            row,
        ) in enumerate(rows):
            for j, item in enumerate(row[1:]):
                self.table.setItem(i, j, QTableWidgetItem(str(item)))
        conn.close()


class UserManagerDialog(QDialog):
    def __init__(self, parent=None):
        dbManager = DatabaseManager()
        super().__init__(parent)
        self.setWindowTitle("Управление пользователями")
        self.setGeometry(100,100,400,300)
        
        layout = QVBoxLayout()
        
        self.user_table = QTableWidget(self)
        self.user_table.setColumnCount(2)
        self.user_table.setHorizontalHeaderLabels(["ID", "Имя пользователя"])
        layout.addWidget(self.user_table)
        
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Добавить", self)
        self.add_button.clicked.connect(self.add_user)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Изменить", self)
        self.edit_button.clicked.connect(self.edit_user)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Удалить", self)
        self.delete_button.clicked.connect(self.delete_user)
        button_layout.addWidget(self.delete_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        dbManager.load_users()
        
    def add_user():
        pass
    
    def edit_user():
        pass
    
    def delete_user():
        pass
        
        
class USBUploader(QMainWindow):
    DEFAULT_FOLDER = "UploadedData"
    dbManager = DatabaseManager()

    def __init__(self):
        super().__init__()
        self.settings_dialog = SettingsDialog(self)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("USB File Uploader")
        self.setGeometry(100, 100, 400, 400)

        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        settings_menu = QMenu("Настройки", self)
        menu_bar.addMenu(settings_menu)

        statistic_menu = QMenu("Статистика", self)
        open_statistic_action = QAction("Открыть статистику", self)
        open_statistic_action.triggered.connect(self.open_statistic)
        statistic_menu.addAction(open_statistic_action)
        menu_bar.addMenu(statistic_menu)

        open_settings_action = QAction("Открыть настройки", self)
        open_settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(open_settings_action)

        open_manage_users_action = QAction("Управление пользователями",self)
        open_manage_users_action.triggered.connect(self.open_user_management)        
        settings_menu.addAction(open_manage_users_action)
        
        reload_list_drives_action = QAction("Обновить список носителей", self)
        reload_list_drives_action.triggered.connect(self.update_usb_list)
        settings_menu.addAction(reload_list_drives_action)
        # Виджеты

        layout = QVBoxLayout()

        self.label = QLabel("Введите ваше имя:")
        layout.addWidget(self.label)

        self.user_name_input = QLineEdit(self)
        layout.addWidget(self.user_name_input)

        self.select_file_button = QPushButton("Выбрать файл", self)
        self.select_file_button.clicked.connect(self.select_file)
        layout.addWidget(self.select_file_button)

        self.usb_selection_layout = QHBoxLayout()

        self.usb_list_label = QLabel("Выберите USB-носитель:")
        self.usb_selection_layout.addWidget(self.usb_list_label)

        self.refresh_button = QPushButton("↻")
        self.refresh_button.clicked.connect(self.update_usb_list)
        self.usb_selection_layout.addWidget(self.refresh_button)
        layout.addLayout(self.usb_selection_layout)

        self.usb_list = QListWidget(self)
        self.update_usb_list()
        layout.addWidget(self.usb_list)

        self.upload_button = QPushButton("Загрузить файл на выбранный USB", self)
        self.upload_button.clicked.connect(self.upload_file)
        layout.addWidget(self.upload_button)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.selected_file = None
        self.copy_thread = None

        bottom_layoyt = QHBoxLayout()

        self.lock_button = QPushButton("🔒")
        self.lock_button.clicked.connect(self.toggle_lock)

        bottom_layoyt.addWidget(self.lock_button)
        bottom_layoyt.addStretch()

        layout.addLayout(bottom_layoyt)

        self.is_locked = True

    def toggle_lock(self):

        if self.is_locked:
            self.lock_button.setText("🔑")
            self.is_locked = False
            print("Открыт")
        else:
            self.lock_button.setText("🔒")
            self.is_locked = True
            print("Закрыт")

    def update_usb_list(self):
        self.usb_list.clear()
        usb_drives = self.find_usb_drives()
        if usb_drives:
            self.usb_list.addItems(usb_drives)
        else:
            self.usb_list.addItem("USB-носители не найдены")

    def select_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл", "", "Все файлы (*)", options=options
        )
        if file_path:
            self.selected_file = file_path
            self.status_label.setText(f"Выбран файл: {os.path.basename(file_path)}")

    def upload_file(self):
        if not self.selected_file:
            self.status_label.setText("Файл не выбран!")
            return
        user_name = self.user_name_input.text()
        if not user_name.strip():
            self.status_label.setText("Введите ваше имя!")
            return
        selected_usb_item = self.usb_list.currentItem()
        if (
            not selected_usb_item
            or selected_usb_item.text() == "USB-носители не найдены"
        ):
            self.status_label.setText("USB-носитель не выбран!")
            return
        usb_path = selected_usb_item.text()
        dest_path = os.path.join(
            usb_path,
            self.settings_dialog.default_folder_input.text(),
            os.path.basename(self.selected_file),
        )

        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Копирование файла...")

        # Запускаем фоновый поток для копирования файла

        self.copy_thread = FileCopyThread(self.selected_file, dest_path)
        self.copy_thread.progress.connect(self.progress_bar.setValue)
        self.copy_thread.finished.connect(self.on_copy_finished)
        self.copy_thread.start()

        # Сохранение лога в базе данных

        file_size = os.path.getsize(self.selected_file)
        dbManager.save_log(user_name, self.selected_file, file_size, usb_path)

    def on_copy_finished(self, message):
        self.status_label.setText(message)
        self.progress_bar.setVisible(False)

    def find_usb_drives(self):
        drives = [
            f"{chr(d)}:\\" for d in range(65, 91) if os.path.exists(f"{chr(d)}:\\")
        ]
        usb_drives = []
        for drive in drives:
            if os.path.exists(os.path.join(drive, "System Volume Information")):
                usb_drives.append(drive)
        return usb_drives

    def open_settings(self):
        self.settings_dialog.exec_()

    def open_statistic(self):
        self.statistics_dialog = StatisticsDialog(self)
        self.statistics_dialog.exec_()
    
    def open_user_management(self):
        self.user_management_dialog = UserManagerDialog(self)
        self.user_management_dialog.exec_()
# Инициализация приложения

if __name__ == "__main__":
    dbManager = DatabaseManager()
    # dbManager.initialize_database()

    app = QApplication([])
    window = USBUploader()
    window.show()
    app.exec_()
