from PyQt6.QtWidgets import QLineEdit, QToolButton, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent


class PasswordEdit(QWidget):
    textChanged = pyqtSignal(str)
    returnPressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                font-size: 14px;
            }
        """)

        self.toggle_button = QToolButton()
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.setText("👁")
        self.toggle_button.setToolTip("Показать пароль")
        self.toggle_button.setFixedSize(30, 30)
        self.toggle_button.setStyleSheet("""
            QToolButton {
                border: none;
                background: transparent;
                font-size: 14px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background: #f0f0f0;
            }
        """)

        layout.addWidget(self.password_edit)
        layout.addWidget(self.toggle_button)

    def setup_connections(self):
        self.toggle_button.toggled.connect(self.toggle_password_visibility)
        self.password_edit.textChanged.connect(self.textChanged.emit)

    def toggle_password_visibility(self, checked):
        if checked:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_button.setToolTip("Скрыть пароль")
            self.toggle_button.setText("🔒")
        else:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_button.setToolTip("Показать пароль")
            self.toggle_button.setText("👁")

    def text(self) -> str:
        return self.password_edit.text()

    def setText(self, text: str):
        self.password_edit.setText(text)

    def setPlaceholderText(self, text: str):
        self.password_edit.setPlaceholderText(text)

    def clear(self):
        self.password_edit.clear()
        self.toggle_button.setChecked(False)

    def setReadOnly(self, read_only: bool):
        self.password_edit.setReadOnly(read_only)
        self.toggle_button.setEnabled(not read_only)

    def setFocus(self):
        self.password_edit.setFocus()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.returnPressed.emit()
        else:
            super().keyPressEvent(event)