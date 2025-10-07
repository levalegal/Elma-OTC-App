import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont

from config import config
from views.login_view import LoginView
from views.main_view import MainView
from auth import auth_manager
from utils.helpers import helpers

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('elma_otk_app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ElmaOTKApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.setup_application()
        self.setup_ui()
        self.setup_connections()

    def setup_application(self):
        self.setWindowTitle(f"{config.ui.APP_NAME} - {config.ui.ORGANIZATION}")
        self.setMinimumSize(1000, 700)

        app = QApplication.instance()
        app.setApplicationName(config.ui.APP_NAME)
        app.setOrganizationName(config.ui.ORGANIZATION)
        app.setApplicationVersion(config.ui.VERSION)

    def setup_ui(self):
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.login_view = LoginView()
        self.main_view = MainView()

        self.stacked_widget.addWidget(self.login_view)
        self.stacked_widget.addWidget(self.main_view)

        self.stacked_widget.setCurrentWidget(self.login_view)
        self.apply_styles()

    def apply_styles(self):
        try:
            # Используем встроенные стили вместо файла
            self.apply_default_styles()
        except Exception as e:
            logger.error(f"Ошибка применения стилей: {e}")
            self.apply_default_styles()

    def apply_default_styles(self):
        default_style = """
            QMainWindow {
                background-color: #f0f0f0;
            }
            QStatusBar {
                background-color: #2c3e50;
                color: white;
                padding: 5px;
            }
            QStatusBar::item {
                border: none;
            }
            QMessageBox {
                background-color: white;
            }
        """
        self.setStyleSheet(default_style)

    def setup_connections(self):
        self.login_view.login_successful.connect(self.handle_login_success)
        self.main_view.logout_requested.connect(self.handle_logout)

    def handle_login_success(self, user_info):
        try:
            self.current_user = user_info
            logger.info(f"Успешный вход пользователя: {user_info['username']}")

            self.main_view.set_user_info(user_info)
            self.stacked_widget.setCurrentWidget(self.main_view)

            self.setWindowTitle(
                f"{config.ui.APP_NAME} - {config.ui.ORGANIZATION} - "
                f"{user_info['full_name']} ({auth_manager.get_role_display_name(user_info['role'])})"
            )

            self.showMaximized()

            helpers.show_info(
                f"Добро пожаловать, {user_info['full_name']}!\n"
                f"Роль: {auth_manager.get_role_display_name(user_info['role'])}",
                self
            )

        except Exception as e:
            logger.error(f"Ошибка при переходе в главное окно: {e}")
            helpers.show_error(f"Ошибка инициализации главного окна: {e}", self)

    def handle_logout(self):
        try:
            if self.current_user:
                logger.info(f"Пользователь {self.current_user['username']} вышел из системы")

            auth_manager.logout()
            self.current_user = None

            self.login_view.clear_form()
            self.stacked_widget.setCurrentWidget(self.login_view)

            self.setWindowTitle(f"{config.ui.APP_NAME} - {config.ui.ORGANIZATION}")
            self.showNormal()

        except Exception as e:
            logger.error(f"Ошибка при выходе из системы: {e}")
            helpers.show_error(f"Ошибка выхода из системы: {e}", self)

    def closeEvent(self, event):
        try:
            if self.current_user:
                reply = helpers.confirm_action(
                    "Подтверждение выхода",
                    "Вы уверены, что хотите выйти из приложения?",
                    self
                )

                if not reply:
                    event.ignore()
                    return

                logger.info(f"Приложение закрыто пользователем: {self.current_user['username']}")
            else:
                logger.info("Приложение закрыто")

            auth_manager.logout()
            event.accept()

        except Exception as e:
            logger.error(f"Ошибка при закрытии приложения: {e}")
            event.accept()


def main():
    try:
        config.setup_directories()
        logger.info("Конфигурация приложения загружена")

        app = QApplication(sys.argv)

        # Убраны несовместимые атрибуты для PyQt6
        app.setFont(QFont("Segoe UI", 10))

        window = ElmaOTKApp()
        window.show()

        logger.info("Приложение успешно запущено")

        return app.exec()

    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске приложения: {e}")

        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Icon.Critical)
        error_msg.setWindowTitle("Ошибка запуска")
        error_msg.setText("Не удалось запустить приложение")
        error_msg.setInformativeText(
            f"Произошла критическая ошибка:\n{str(e)}\n\n"
            "Пожалуйста, обратитесь к администратору."
        )
        error_msg.exec()

        return 1


if __name__ == "__main__":
    sys.exit(main())