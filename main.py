import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QCheckBox,
    QMessageBox,
    QFileDialog,
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap
from src.assets.reorder import CSVReorder, create_reorder_config
from src.uiitems.close_button import CloseButton


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class MainWorkflowApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.input_csv_file_path = None
        self.output_directory = None
        self.sort_columns = None
        self.use_language_sorting = False
        self.reverse = False
        self.setMouseTracking(True)
        self.oldPos = self.pos()

    def init_ui(self):
        """初始化用户界面。"""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName("App")

        self.setStyleSheet(
            """
            QWidget {
                font-family: 'Arial';
                background-color: transparent; 
                border: 2px solid #CDEBF0; 
                border-radius: 20px;
            }
            QPushButton {
                background-color: #CDEBF0;
                color: black;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #BEE0E8;
            }
            QLabel#Logo {
                background-color: transparent;
            }
            QMessageBox {
                background-color: #CDEBF0;
                color: black;
                font-size: 16px;
                border: 2px solid #BEE0E8;
                border-radius: 12px;
            }
            QMessageBox QPushButton {
                background-color: #CDEBF0;
                color: black;
                font-weight: bold;
                border: 2px solid #BEE0E8;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 80px;
                min-height: 35px;
            }
            QMessageBox QPushButton:hover {
                background-color: #BEE0E8;
            }
        """
        )

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(5, 5, 5, 5)
        self.mainLayout.setSpacing(10)
        self.mainLayout.addLayout(self.create_title_bar())
        self.logoLabel = self.create_logo_label()
        self.mainLayout.addWidget(self.logoLabel)

        self.csv_file_button = self.create_button(
            "Select CSV File", self.select_csv_file
        )
        self.mainLayout.addWidget(self.csv_file_button)
        self.output_dir_button = self.create_button(
            "Select Output Directory", self.select_output_directory
        )
        self.mainLayout.addWidget(self.output_dir_button)

        self.sort_columns_input = self.create_line_edit(
            "Enter sort columns (comma-separated)"
        )
        self.mainLayout.addWidget(self.sort_columns_input)

        # Create horizontal layout for checkboxes
        checkbox_layout = QHBoxLayout()

        # Updated checkbox style to match button background
        checkbox_style = """
            QCheckBox {
                background-color: #CDEBF0;
                color: black;
                font-weight: bold;
                padding: 10px;
                margin: 5px;
                border-radius: 8px;
                border: 2px solid #BEE0E8;
            }
            QCheckBox:hover {
                background-color: #BEE0E8;
            }
            QCheckBox::indicator {
                background-color: white;
                border: 2px solid #BEE0E8;
                width: 16px;
                height: 16px;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #4A90E2;
                border: 2px solid #4A90E2;
            }
        """

        self.use_language_sorting_checkbox = QCheckBox("Use Language Sorting", self)
        self.use_language_sorting_checkbox.setStyleSheet(checkbox_style)
        self.use_language_sorting_checkbox.stateChanged.connect(
            self.toggle_language_sorting
        )
        checkbox_layout.addWidget(self.use_language_sorting_checkbox)

        self.reverse_sorting_checkbox = QCheckBox("Reverse Sorting", self)
        self.reverse_sorting_checkbox.setStyleSheet(checkbox_style)
        self.reverse_sorting_checkbox.stateChanged.connect(self.toggle_reverse_sorting)
        checkbox_layout.addWidget(self.reverse_sorting_checkbox)

        self.mainLayout.addLayout(checkbox_layout)

        self.start_button = self.create_button(
            "Start Cooking", self.run_reorder_csv_workflow
        )
        self.mainLayout.addWidget(self.start_button)

        self.setLayout(self.mainLayout)
        self.resize(540, 880)

    def create_button(self, text, slot, style=None):
        """创建按钮并设置点击事件。"""
        button = QPushButton(text, self)
        button.clicked.connect(slot)
        button.setStyleSheet(
            style
            if style
            else """
            QPushButton {
                background-color: #CDEBF0;
                color: black;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #BEE0E8;
            }
        """
        )
        return button

    def create_line_edit(self, placeholder, style=None):
        line_edit = QLineEdit(self)
        line_edit.setPlaceholderText(placeholder)
        line_edit.setStyleSheet(
            style
            if style
            else """
            QLineEdit {
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                margin: 10px;
                color: black;
                background-color: white;
            }
        """
        )
        return line_edit

    def show_custom_message(self):
        """显示自定义消息框。"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText("The workflow has been completed successfully.")
        msg.setWindowTitle("Success")
        msg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.CustomizeWindowHint)
        msg.setStyleSheet(
            """
            QMessageBox {
                background-color: #CDEBF0;
                color: black;
                font-size: 16px;
                border: 2px solid #BEE0E8;
                border-radius: 12px;
            }
            QMessageBox QPushButton {
                background-color: #CDEBF0;
                color: black;
                font-weight: bold;
                border: 2px solid #BEE0E8;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 80px;
                min-height: 35px;
            }
            QMessageBox QPushButton:hover {
                background-color: #BEE0E8;
            }
            """
        )
        msg.exec_()

    def create_title_bar(self):
        """创建标题栏。"""
        title_bar = QHBoxLayout()
        close_button = CloseButton(self)
        close_button.clicked.connect(self.close)  # Connect close button to close event
        title_bar.addWidget(close_button, alignment=Qt.AlignRight)
        return title_bar

    def create_logo_label(self):
        """创建 Logo 标签。"""
        logo = QLabel(self)
        cover_path = get_resource_path(os.path.join("static", "cover.png"))
        pixmap = QPixmap(cover_path).scaled(500, 800)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)
        logo.setObjectName("Logo")
        return logo

    def select_csv_file(self):
        """选择 CSV 文件。"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv)"
        )
        if file_path:
            self.input_csv_file_path = file_path

    def select_output_directory(self):
        """选择输出目录。"""
        directory_path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory"
        )
        if directory_path:
            self.output_directory = directory_path

    def toggle_language_sorting(self, state):
        """切换语言排序。"""
        self.use_language_sorting = state == Qt.Checked

    def toggle_language_column(self, state):
        """切换语言列。"""
        self.language_column = state == Qt.Checked

    def toggle_reverse_sorting(self, state):
        """切换反向排序。"""
        self.reverse = state == Qt.Checked

    def run_reorder_csv_workflow(self):
        """运行重新排序 CSV 工作流程。"""
        if not self.input_csv_file_path or not self.output_directory:
            QMessageBox.warning(
                self, "Error", "Please select a CSV file and output directory."
            )
            return

        sort_columns_text = self.sort_columns_input.text()
        if not sort_columns_text.strip():
            QMessageBox.warning(self, "Error", "Please enter at least one sort column.")
            return

        # Parse sort columns from user input
        sort_columns = []
        for col in sort_columns_text.split(","):
            col = col.strip()
            if col:
                # For now, treat all columns as non-date. You could add a UI option to specify date columns
                sort_columns.append((col, False))

        try:
            # Create configuration using the new class-based approach
            config = create_reorder_config(
                sort_columns=sort_columns,
                reverse=self.reverse,
                use_language_sorting=self.use_language_sorting,
                output_prefix="sorted_",
            )

            # Create CSV reorder instance
            reorder_util = CSVReorder(config)

            # Perform the reordering using the safe method
            result = reorder_util.reorder_csv_safe(
                self.input_csv_file_path, self.output_directory
            )

            if result:
                QMessageBox.information(
                    self,
                    "Success",
                    f"CSV file has been reordered and saved as:\n{result}",
                )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "CSV reordering failed. Please check the console for error messages.",
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def mousePressEvent(self, event):
        """鼠标按下事件。"""
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        """鼠标移动事件。"""
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def closeEvent(self, event):
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWorkflowApp()
    window.show()
    sys.exit(app.exec_())
