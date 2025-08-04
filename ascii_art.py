import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QTextEdit, QFileDialog, QWidget, QSlider, QLabel, QComboBox, QMessageBox,
                           QSplitter, QFrame, QSizePolicy)
from PyQt6.QtGui import QFont, QPixmap, QImage, QIcon
from PyQt6.QtCore import Qt, QSize
from PIL import Image, ImageQt
import io
ASCII_CHARS = [
    "$", "@", "B", "%", "8", "&", "W", "M", "#", "*", "o", "a", "h", "k", "b", "d", 
    "p", "q", "w", "m", "Z", "O", "0", "Q", "L", "C", "J", "U", "Y", "X", "z", "c", 
    "v", "u", "n", "x", "r", "j", "f", "t", "/", "\\", "|", "(", ")", "1", "{", "}", 
    "[", "]", "?", "-", "_", "+", "~", "<", ">", "i", "!", "l", "I", ";", ":", ",", 
    "\"", "^", "`", "'", ".", " "
]
def resize_image(image, new_width=100):
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.5)
    if new_height < 1:
        new_height = 1
    return image.resize((new_width, new_height))
def grayify(image):
    return image.convert("L")
def pixels_to_ascii(image, char_set):
    pixels = list(image.getdata())
    max_pixel_value = 255
    step = max_pixel_value / (len(char_set) - 1)
    ascii_str = ""
    for pixel in pixels:
        index = int(pixel / step)
        if index >= len(char_set):
            index = len(char_set) - 1
        ascii_str += char_set[index]
    return ascii_str
def image_to_ascii(path, width=100, char_set=ASCII_CHARS):
    try:
        image = Image.open(path)
    except Exception as e:
        return f"Не удалось открыть изображение: {str(e)}"
    image = resize_image(image, width)
    image = grayify(image)
    ascii_str = pixels_to_ascii(image, char_set)
    ascii_img = ""
    for i in range(0, len(ascii_str), image.width):
        ascii_img += ascii_str[i:i + image.width] + "\n"
    return ascii_img
def pil2pixmap(pil_image):
    bytes_img = io.BytesIO()
    pil_image.save(bytes_img, format='PNG')
    bytes_img.seek(0)
    return QPixmap.fromImage(QImage.fromData(bytes_img.getvalue()))
class StyledButton(QPushButton):
    def __init__(self, text, parent=None, icon=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(24, 24))
        self.setStyleSheet("""
            QPushButton {
                background-color: #2e5fb3;
                color: white;
                border-radius: 8px;
                border: none;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #3a70ca;
            }
            QPushButton:pressed {
                background-color: #22498d;
            }
        """)
class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(200, 200)  
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 8px;
                color: #cccccc;
            }
        """)
    def setPixmap(self, pixmap):
        scaled_pixmap = pixmap.scaled(self.width(), self.height(), 
                                      Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
        super().setPixmap(scaled_pixmap)
    def resizeEvent(self, event):
        if self.pixmap():
            scaled_pixmap = self.pixmap().scaled(self.width(), self.height(), 
                                          Qt.AspectRatioMode.KeepAspectRatio, 
                                          Qt.TransformationMode.SmoothTransformation)
            super().setPixmap(scaled_pixmap)
        super().resizeEvent(event)
class AsciiArtApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_path = None
        self.original_image = None
        self.setWindowTitle("ASCII Art Преобразователь")
        self.setGeometry(100, 100, 1000, 700)
        try:
            self.setWindowIcon(QIcon("ascii_art.png"))
        except Exception:
            pass
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 8px;
                font-family: Courier;
                padding: 10px;
                color: #e0e0e0;
            }
            QLabel {
                font-family: Arial;
                font-weight: bold;
                color: #e0e0e0;
            }
            QSlider {
                height: 20px;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #444;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4a6ea9;
                border: none;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QComboBox {
                padding: 6px;
                border-radius: 4px;
                border: 1px solid #444;
                background-color: #2d2d2d;
                color: #e0e0e0;
                min-width: 180px;
                height: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #e0e0e0;
                selection-background-color: #4a6ea9;
            }
            QSplitter::handle {
                background-color: #444;
            }
            QMessageBox {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
        """)
        self.setup_ui()
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        top_panel = QHBoxLayout()
        icon = None
        try:
            icon = QIcon("ascii_art.png")
        except Exception:
            icon = None
        self.load_button = StyledButton("Загрузить изображение", icon=icon)
        self.load_button.clicked.connect(self.load_image)
        top_panel.addWidget(self.load_button)
        width_layout = QHBoxLayout()
        width_label = QLabel("Ширина:")
        width_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        width_layout.addWidget(width_label)
        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setRange(20, 200)
        self.width_slider.setValue(100)
        self.width_slider.valueChanged.connect(self.update_ascii_art)
        width_layout.addWidget(self.width_slider)
        self.width_label = QLabel("100")
        self.width_label.setFont(QFont("Arial", 10))
        self.width_label.setMinimumWidth(30)
        width_layout.addWidget(self.width_label)
        top_panel.addLayout(width_layout)
        self.set_label = QLabel("Набор символов:")
        self.set_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        top_panel.addWidget(self.set_label)
        self.char_set_combo = QComboBox()
        self.char_set_combo.addItem("Полный набор (70 символов)")
        self.char_set_combo.addItem("Стандартный (@%#*+=-:. )")
        self.char_set_combo.addItem("Простой (▓▒░ )")
        self.char_set_combo.currentIndexChanged.connect(self.update_ascii_art)
        top_panel.addWidget(self.char_set_combo)
        main_layout.addLayout(top_panel)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(8)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #444;
                border-radius: 3px;
                margin: 1px;
            }
        """)
        image_container = QWidget()
        image_layout = QVBoxLayout(image_container)
        image_title = QLabel("Исходное изображение")
        image_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        image_layout.addWidget(image_title)
        self.image_label = ImageLabel()
        image_layout.addWidget(self.image_label)
        ascii_container = QWidget()
        ascii_layout = QVBoxLayout(ascii_container)
        ascii_title = QLabel("ASCII Art")
        ascii_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ascii_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        ascii_layout.addWidget(ascii_title)
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Courier", 9))
        self.text_edit.setReadOnly(True)
        ascii_layout.addWidget(self.text_edit)
        splitter.addWidget(image_container)
        splitter.addWidget(ascii_container)
        splitter.setSizes([300, 700])  
        main_layout.addWidget(splitter, 1)  
        bottom_panel = QHBoxLayout()
        self.copy_button = StyledButton("Копировать в буфер обмена")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        bottom_panel.addWidget(self.copy_button)
        self.save_button = StyledButton("Сохранить в файл")
        self.save_button.clicked.connect(self.save_to_file)
        bottom_panel.addWidget(self.save_button)
        main_layout.addLayout(bottom_panel)
        self.text_edit.setPlainText("Загрузите изображение, чтобы создать ASCII Art")
        self.image_label.setText("Здесь будет ваше изображение")
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Выбрать изображение", 
            "", 
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            try:
                self.image_path = file_path
                self.original_image = Image.open(file_path)
                pixmap = pil2pixmap(self.original_image)
                self.image_label.setPixmap(pixmap)
                self.update_ascii_art()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть изображение: {str(e)}")
    def get_current_charset(self):
        index = self.char_set_combo.currentIndex()
        if index == 0:
            return ASCII_CHARS
        elif index == 1:
            return ["@", "%", "#", "*", "+", "=", "-", ":", ".", " "]
        elif index == 2:
            return ["▓", "▒", "░", " "]
        return ASCII_CHARS
    def update_ascii_art(self):
        if not self.image_path or not self.original_image:
            return
        width = self.width_slider.value()
        self.width_label.setText(str(width))
        charset = self.get_current_charset()
        ascii_art = image_to_ascii(self.image_path, width, charset)
        self.text_edit.setPlainText(ascii_art)
    def copy_to_clipboard(self):
        text = self.text_edit.toPlainText()
        if text:
            self.text_edit.selectAll()
            self.text_edit.copy()
            cursor = self.text_edit.textCursor()
            cursor.clearSelection()
            self.text_edit.setTextCursor(cursor)
            QMessageBox.information(self, "Скопировано", "ASCII Art скопирован в буфер обмена")
    def save_to_file(self):
        if not self.text_edit.toPlainText() or self.text_edit.toPlainText() == "Загрузите изображение, чтобы создать ASCII Art":
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить ASCII Art",
            "",
            "Текстовые файлы (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.text_edit.toPlainText())
                QMessageBox.information(self, "Сохранено", "ASCII Art успешно сохранен в файл")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении файла: {str(e)}")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AsciiArtApp()
    window.show()
    sys.exit(app.exec()) 
