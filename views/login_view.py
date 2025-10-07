from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFrame, QMessageBox,
                             QApplication, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from auth import auth_manager
from widgets.password_edit import PasswordEdit
from utils.helpers import helpers


class LoginView(QWidget):
    login_successful = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setWindowTitle("Elma_OTK_App - Авторизация")
        self.setMinimumSize(400, 500)  # Минимальный размер вместо фиксированного

        # Получаем размер экрана
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # Устанавливаем размер как процент от экрана
        width = min(500, int(screen_geometry.width() * 0.4))
        height = min(600, int(screen_geometry.height() * 0.7))
        self.resize(width, height)

        # Основной контейнер
        main_widget = QWidget()
        main_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

        main_layout = QVBoxLayout(main_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        # Логотип и заголовок
        logo_layout = QVBoxLayout()
        logo_layout.setSpacing(15)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Иконка приложения
        icon_label = QLabel("ELMA")
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: white;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 60px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                min-width: 120px;
                min-height: 120px;
                max-width: 120px;
                max-height: 120px;
            }
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(120, 120)

        title_label = QLabel("Elma OTC")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                background: transparent;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel("Система технического контроля")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 14px;
                background: transparent;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_layout.addWidget(icon_label)
        logo_layout.addWidget(title_label)
        logo_layout.addWidget(subtitle_label)

        main_layout.addLayout(logo_layout)
        main_layout.addSpacing(40)

        # Карточка формы входа - делаем адаптивной
        login_card = QFrame()
        login_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        login_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        card_layout = QVBoxLayout(login_card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(20)

        # Заголовок формы
        form_title = QLabel("Вход в систему")
        form_title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 20px;
                font-weight: bold;
                background: transparent;
            }
        """)
        form_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Поле логина
        username_layout = QVBoxLayout()
        username_layout.setSpacing(8)

        username_label = QLabel("Логин:")
        username_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 600;
                background: transparent;
            }
        """)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Введите ваш логин")
        self.username_edit.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
                color: #2c3e50;
                selection-background-color: #3498db;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background: white;
            }
            QLineEdit::placeholder {
                color: #95a5a6;
            }
        """)
        self.username_edit.setMinimumHeight(45)

        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit)

        # Поле пароля
        password_layout = QVBoxLayout()
        password_layout.setSpacing(8)

        password_label = QLabel("Пароль:")
        password_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 600;
                background: transparent;
            }
        """)

        self.password_edit = PasswordEdit()
        self.password_edit.setPlaceholderText("Введите ваш пароль")
        self.password_edit.setStyleSheet("""
            PasswordEdit {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
                color: #2c3e50;
                selection-background-color: #3498db;
            }
            PasswordEdit:focus {
                border-color: #3498db;
                background: white;
            }
            PasswordEdit::placeholder {
                color: #95a5a6;
            }
        """)
        self.password_edit.setMinimumHeight(45)

        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)

        # Сообщение об ошибке
        self.error_label = QLabel()
        self.error_label.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 12px;
                background: #fadbd8;
                border: 1px solid #f5b7b1;
                border-radius: 6px;
                padding: 10px 12px;
            }
        """)
        self.error_label.setVisible(False)
        self.error_label.setWordWrap(True)

        # Кнопка входа
        self.login_button = QPushButton("Войти в систему")
        self.login_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 14px;
                font-size: 16px;
                font-weight: bold;
                min-height: 50px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2980b9, stop:1 #2471a3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2471a3, stop:1 #1b4f72);
            }
            QPushButton:disabled {
                background: #bdc3c7;
                color: #7f8c8d;
            }
        """)

        # Футер
        footer_label = QLabel("© 2024 ООО «СПбЦ «ЭЛМА». Все права защищены.")
        footer_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.6);
                font-size: 11px;
                background: transparent;
                margin-top: 10px;
            }
        """)
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Собираем карточку
        card_layout.addWidget(form_title)
        card_layout.addSpacing(10)
        card_layout.addLayout(username_layout)
        card_layout.addLayout(password_layout)
        card_layout.addWidget(self.error_label)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.login_button)

        # Собираем основное окно
        main_layout.addWidget(login_card)
        main_layout.addSpacing(20)
        main_layout.addWidget(footer_label)

        # Устанавливаем основной виджет
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_widget)

    def setup_connections(self):
        self.login_button.clicked.connect(self.handle_login)
        self.username_edit.returnPressed.connect(self.handle_login)
        self.password_edit.returnPressed.connect(self.handle_login)

        self.username_edit.textChanged.connect(self.clear_error)
        self.password_edit.textChanged.connect(self.clear_error)

    def showEvent(self, event):
        super().showEvent(event)
        # Центрируем окно при показе
        self.center_on_screen()
        self.username_edit.setFocus()

    def center_on_screen(self):
        """Центрирует окно на экране"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()

        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def handle_login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()

        if not username:
            self.show_error("Введите логин")
            self.username_edit.setFocus()
            return

        if not password:
            self.show_error("Введите пароль")
            self.password_edit.setFocus()
            return

        # Блокируем кнопку во время авторизации
        self.login_button.setEnabled(False)
        self.login_button.setText("Вход...")

        try:
            user_info = auth_manager.login(username, password)
            self.login_successful.emit(user_info)

        except Exception as e:
            self.show_error(str(e))
            self.reset_login_button()

    def show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def clear_error(self):
        self.error_label.setVisible(False)

    def reset_login_button(self):
        self.login_button.setEnabled(True)
        self.login_button.setText("Войти в систему")

    def clear_form(self):
        self.username_edit.clear()
        self.password_edit.clear()
        self.clear_error()
        self.reset_login_button()
        self.username_edit.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)