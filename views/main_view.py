from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTabWidget, QStatusBar, QToolBar,
                             QMainWindow, QSizePolicy, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QPixmap, QFont

from auth import auth_manager
from views.order_view import OrderView
from views.client_view import ClientView
from views.report_view import ReportView
from utils.helpers import helpers


class MainView(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.user_info = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Elma_OTK_App - Главная")
        self.setMinimumSize(1200, 800)

        self.setup_toolbar()
        self.setup_central_widget()
        self.setup_statusbar()
        self.apply_styles()

    def setup_toolbar(self):
        toolbar = QToolBar("Основная панель")
        toolbar.setMovable(False)
        toolbar.setIconSize(QPixmap(24, 24).size())  # Исправлено здесь
        self.addToolBar(toolbar)

        self.user_action = QAction("Пользователь", self)
        self.user_action.setEnabled(False)

        self.logout_action = QAction("Выйти", self)
        self.logout_action.triggered.connect(self.handle_logout)

        toolbar.addAction(self.user_action)
        toolbar.addSeparator()
        toolbar.addAction(self.logout_action)

    def setup_central_widget(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header_frame = QFrame()
        header_frame.setObjectName("header_frame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)

        title_label = QLabel("ИС Отдел технического контроля")
        title_label.setObjectName("title_label")

        self.user_label = QLabel()
        self.user_label.setObjectName("user_label")
        self.user_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.user_label)

        main_layout.addWidget(header_frame)

        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("main_tabs")
        self.tab_widget.setDocumentMode(True)

        self.order_view = OrderView()
        self.client_view = ClientView()
        self.report_view = ReportView()

        self.tab_widget.addTab(self.order_view, "Формирование заказа")
        self.tab_widget.addTab(self.client_view, "Управление клиентами")
        self.tab_widget.addTab(self.report_view, "Отчеты")

        main_layout.addWidget(self.tab_widget)

    def setup_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_label = QLabel("Готов")
        self.status_bar.addWidget(self.status_label)

        self.user_status_label = QLabel()
        self.user_status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.status_bar.addPermanentWidget(self.user_status_label)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QFrame#header_frame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                border-bottom: 2px solid #1a252f;
            }
            QLabel#title_label {
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 5px;
            }
            QLabel#user_label {
                color: #ecf0f1;
                font-size: 14px;
                padding: 5px;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
                border-radius: 4px;
                margin: 0px;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                border: 1px solid #c0c0c0;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
                font-weight: bold;
                color: #555;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-color: #c0c0c0;
                border-bottom-color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #f0f0f0;
            }
            QStatusBar {
                background-color: #34495e;
                color: white;
                padding: 5px;
            }
            QStatusBar QLabel {
                color: white;
                padding: 2px 8px;
            }
            QToolBar {
                background-color: #ecf0f1;
                border: none;
                border-bottom: 1px solid #bdc3c7;
                spacing: 5px;
                padding: 3px;
            }
            QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 5px 10px;
                color: #2c3e50;
            }
            QToolButton:hover {
                background-color: #d5dbdb;
                border: 1px solid #a6acaf;
            }
            QToolButton:pressed {
                background-color: #a6acaf;
            }
        """)

    def set_user_info(self, user_info):
        self.user_info = user_info

        role_display = auth_manager.get_role_display_name(user_info['role'])
        user_text = f"{user_info['full_name']} ({role_display})"

        self.user_label.setText(user_text)
        self.user_action.setText(user_text)
        self.user_status_label.setText(user_text)

        self.update_permissions()

    def update_permissions(self):
        if not self.user_info:
            return

        permissions = auth_manager.get_user_permissions()

        if not permissions.get('can_view_orders'):
            self.tab_widget.setTabEnabled(1, False)

        if not permissions.get('can_generate_reports'):
            self.tab_widget.setTabEnabled(2, False)

        self.order_view.update_permissions(permissions)
        self.client_view.update_permissions(permissions)
        self.report_view.update_permissions(permissions)

    def handle_logout(self):
        reply = helpers.confirm_action(
            "Подтверждение выхода",
            "Вы уверены, что хотите выйти из системы?",
            self
        )

        if reply:
            self.logout_requested.emit()

    def showEvent(self, event):
        super().showEvent(event)
        if self.user_info:
            self.status_label.setText("Добро пожаловать в систему")

    def closeEvent(self, event):
        self.handle_logout()
        event.ignore()