"""
Конфигурационный модуль приложения Elma_OTK_App
Содержит настройки базы данных, пути и константы приложения
"""

import os
import sys
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class DatabaseConfig:
    """Конфигурация базы данных"""
    DATABASE_NAME: str = "elma_otk.db"
    DATABASE_VERSION: str = "1.0"

    def hash_password(self, password: str) -> str:
        """Хеширование пароля (добавлен этот метод)"""
        return hashlib.sha256(password.encode()).hexdigest()

    # Таблицы базы данных
    TABLES: Dict = field(default_factory=lambda: {
        'users': """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('manager', 'lab_assistant', 'controller')),
                full_name TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        'clients': """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_type TEXT NOT NULL CHECK(client_type IN ('legal', 'individual')),
                company_name TEXT,
                address TEXT,
                inn TEXT,
                bank_account TEXT,
                bik TEXT,
                director_name TEXT,
                contact_person TEXT,
                full_name TEXT,
                birth_date DATE,
                passport_series TEXT,
                passport_number TEXT,
                phone TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(inn) WHERE client_type = 'legal',
                UNIQUE(passport_series, passport_number) WHERE client_type = 'individual'
            )
        """,
        'services': """
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        'orders': """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vessel_code TEXT UNIQUE NOT NULL,
                client_id INTEGER NOT NULL,
                order_date DATE NOT NULL,
                total_amount DECIMAL(10, 2) NOT NULL,
                status TEXT DEFAULT 'new' CHECK(status IN ('new', 'in_progress', 'completed', 'cancelled')),
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id),
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        """,
        'order_services': """
            CREATE TABLE IF NOT EXISTS order_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                unit_price DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
                FOREIGN KEY (service_id) REFERENCES services (id),
                UNIQUE(order_id, service_id)
            )
        """
    })

    # Начальные данные - теперь с хешированными паролями
    @property
    def INITIAL_DATA(self):
        """Генерируем начальные данные с хешированными паролями"""
        password_hash = self.hash_password("123456")  # Хешируем пароль
        return {
            'users': [
                ('manager1', password_hash, 'manager', 'Иванов Петр Сергеевич'),
                ('lab1', password_hash, 'lab_assistant', 'Сидорова Мария Ивановна'),
                ('controller1', password_hash, 'controller', 'Петров Алексей Владимирович')
            ],
            'services': [
                ('Химический анализ состава', 'Полный химический анализ материала', 15000.00),
                ('Механические испытания', 'Испытания на прочность и упругость', 25000.00),
                ('Термические испытания', 'Испытания при различных температурах', 18000.00),
                ('Радиографический контроль', 'Контроль с помощью рентгеновского излучения', 32000.00),
                ('Ультразвуковой контроль', 'Контроль ультразвуковым дефектоскопом', 28000.00)
            ]
        }

@dataclass
class UIConfig:
    """Конфигурация пользовательского интерфейса"""
    APP_NAME: str = "Elma_OTK_App"
    ORGANIZATION: str = "ООО «СПбЦ «ЭЛМА»"
    VERSION: str = "1.0.0"

    # Размеры окон
    LOGIN_WINDOW_SIZE: tuple = (400, 300)
    MAIN_WINDOW_SIZE: tuple = (1200, 800)
    DIALOG_MIN_SIZE: tuple = (600, 400)

    # Пути к UI файлам
    UI_DIR: Path = field(default_factory=lambda: Path(__file__).parent / "ui")
    STYLES_FILE: Path = field(default_factory=lambda: Path(__file__).parent / "ui" / "styles.qss")

@dataclass
class AppConfig:
    """Основная конфигурация приложения"""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    ui: UIConfig = field(default_factory=UIConfig)

    # Настройки приложения
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Настройки безопасности
    PASSWORD_MIN_LENGTH: int = 6
    SESSION_TIMEOUT: int = 3600  # 1 час в секундах

    def get_project_root(self) -> Path:
        """Возвращает корневую директорию проекта"""
        return Path(__file__).parent

    def get_database_path(self) -> str:
        """Возвращает полный путь к файлу базы данных"""
        return str(self.get_project_root() / self.database.DATABASE_NAME)

    def setup_directories(self) -> None:
        """Создает необходимые директории"""
        directories = [
            self.get_project_root() / "ui",
            self.get_project_root() / "views",
            self.get_project_root() / "models",
            self.get_project_root() / "widgets",
            self.get_project_root() / "utils",
            self.get_project_root() / "tests",
            self.get_project_root() / "docs"
        ]

        for directory in directories:
            directory.mkdir(exist_ok=True)

# Глобальный объект конфигурации
config = AppConfig()

if __name__ == "__main__":
    # Тестирование конфигурации
    config.setup_directories()
    print("Конфигурация загружена успешно")
    print(f"Корневая директория: {config.get_project_root()}")
    print(f"Путь к БД: {config.get_database_path()}")
    print(f"Хеш пароля '123456': {config.database.hash_password('123456')}")