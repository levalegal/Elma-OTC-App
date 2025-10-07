import sqlite3
import logging
from pathlib import Path
from typing import List, Tuple, Any, Optional, Dict
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.get_database_path()
        self._init_database()

    def _init_database(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Сначала создаем таблицы без сложных constraints
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        role TEXT NOT NULL,
                        full_name TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS clients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        client_type TEXT NOT NULL,
                        company_name TEXT,
                        address TEXT,
                        inn TEXT UNIQUE,
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
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS services (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        price DECIMAL(10, 2) NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        vessel_code TEXT UNIQUE NOT NULL,
                        client_id INTEGER NOT NULL,
                        order_date DATE NOT NULL,
                        total_amount DECIMAL(10, 2) NOT NULL,
                        status TEXT DEFAULT 'new',
                        created_by INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP,
                        FOREIGN KEY (client_id) REFERENCES clients (id),
                        FOREIGN KEY (created_by) REFERENCES users (id)
                    )
                """)

                cursor.execute("""
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
                """)

                self._insert_initial_data(cursor)
                conn.commit()

        except sqlite3.Error as e:
            logger.error(f"Ошибка инициализации БД: {e}")
            raise

    def _insert_initial_data(self, cursor):
        # Проверяем и добавляем пользователей
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            from config import config  # Добавляем импорт
            for user_data in config.database.INITIAL_DATA['users']:
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
                    user_data
                )
            logger.info("Начальные данные пользователей добавлены")

        # Проверяем и добавляем услуги
        cursor.execute("SELECT COUNT(*) FROM services")
        if cursor.fetchone()[0] == 0:
            from config import config  # Добавляем импорт
            for service in config.database.INITIAL_DATA['services']:
                cursor.execute(
                    "INSERT INTO services (name, description, price) VALUES (?, ?, ?)",
                    service
                )
            logger.info("Начальные данные услуг добавлены")

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn

    def execute_query(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            raise

    def execute_insert(self, query: str, params: Tuple = ()) -> int:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Ошибка выполнения вставки: {e}")
            raise

    def execute_update(self, query: str, params: Tuple = ()) -> int:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"Ошибка выполнения обновления: {e}")
            raise

    def user_exists(self, username: str) -> bool:
        result = self.execute_query(
            "SELECT 1 FROM users WHERE username = ? AND is_active = 1",
            (username,)
        )
        return len(result) > 0

    def verify_password(self, username: str, password_hash: str) -> bool:
        result = self.execute_query(
            "SELECT 1 FROM users WHERE username = ? AND password_hash = ? AND is_active = 1",
            (username, password_hash)
        )
        return len(result) > 0

    def get_user_role(self, username: str) -> Optional[str]:
        result = self.execute_query(
            "SELECT role FROM users WHERE username = ? AND is_active = 1",
            (username,)
        )
        return result[0]['role'] if result else None

    def get_user_info(self, username: str) -> Optional[Dict]:
        result = self.execute_query(
            "SELECT id, username, role, full_name FROM users WHERE username = ? AND is_active = 1",
            (username,)
        )
        return dict(result[0]) if result else None

    def get_services(self) -> List[Dict]:
        result = self.execute_query(
            "SELECT id, name, description, price FROM services WHERE is_active = 1 ORDER BY name"
        )
        return [dict(row) for row in result]

    def get_clients(self, client_type: str = None) -> List[Dict]:
        query = "SELECT * FROM clients WHERE 1=1"
        params = []

        if client_type:
            query += " AND client_type = ?"
            params.append(client_type)

        query += " ORDER BY company_name, full_name"
        result = self.execute_query(query, tuple(params))
        return [dict(row) for row in result]

    def search_clients(self, search_term: str, client_type: str = None) -> List[Dict]:
        query = """
            SELECT * FROM clients 
            WHERE (company_name LIKE ? OR full_name LIKE ? OR inn LIKE ? OR phone LIKE ?)
        """
        params = [f"%{search_term}%"] * 4

        if client_type:
            query += " AND client_type = ?"
            params.append(client_type)

        query += " ORDER BY company_name, full_name"
        result = self.execute_query(query, tuple(params))
        return [dict(row) for row in result]

    def get_last_order_id(self) -> int:
        result = self.execute_query("SELECT MAX(id) as last_id FROM orders")
        return result[0]['last_id'] or 0 if result else 0

    def vessel_code_exists(self, vessel_code: str) -> bool:
        result = self.execute_query(
            "SELECT 1 FROM orders WHERE vessel_code = ?",
            (vessel_code,)
        )
        return len(result) > 0

    def create_client(self, client_data: Dict) -> int:
        fields = []
        values = []
        placeholders = []

        for field, value in client_data.items():
            if value is not None:
                fields.append(field)
                values.append(value)
                placeholders.append("?")

        query = f"INSERT INTO clients ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
        return self.execute_insert(query, tuple(values))

    def create_order(self, order_data: Dict, services: List[Dict]) -> int:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                order_fields = ['vessel_code', 'client_id', 'order_date', 'total_amount', 'created_by']
                order_values = [order_data[field] for field in order_fields]
                order_placeholders = ['?' for _ in order_fields]

                order_query = f"""
                    INSERT INTO orders ({', '.join(order_fields)}) 
                    VALUES ({', '.join(order_placeholders)})
                """
                cursor.execute(order_query, order_values)
                order_id = cursor.lastrowid

                for service in services:
                    service_query = """
                        INSERT INTO order_services (order_id, service_id, quantity, unit_price)
                        VALUES (?, ?, ?, ?)
                    """
                    cursor.execute(service_query, (
                        order_id,
                        service['service_id'],
                        service.get('quantity', 1),
                        service['unit_price']
                    ))

                conn.commit()
                return order_id

        except sqlite3.Error as e:
            logger.error(f"Ошибка создания заказа: {e}")
            raise

    def get_orders(self, filters: Dict = None) -> List[Dict]:
        query = """
            SELECT 
                o.id, o.vessel_code, o.order_date, o.total_amount, o.status,
                c.client_type, 
                CASE 
                    WHEN c.client_type = 'legal' THEN c.company_name 
                    ELSE c.full_name 
                END as client_name,
                u.full_name as created_by_name
            FROM orders o
            LEFT JOIN clients c ON o.client_id = c.id
            LEFT JOIN users u ON o.created_by = u.id
            WHERE 1=1
        """
        params = []

        if filters:
            if filters.get('status'):
                query += " AND o.status = ?"
                params.append(filters['status'])
            if filters.get('date_from'):
                query += " AND o.order_date >= ?"
                params.append(filters['date_from'])
            if filters.get('date_to'):
                query += " AND o.order_date <= ?"
                params.append(filters['date_to'])
            if filters.get('vessel_code'):
                query += " AND o.vessel_code LIKE ?"
                params.append(f"%{filters['vessel_code']}%")

        query += " ORDER BY o.order_date DESC, o.id DESC"
        result = self.execute_query(query, tuple(params))
        return [dict(row) for row in result]

    def get_order_details(self, order_id: int) -> Dict:
        order_result = self.execute_query("""
            SELECT o.*, 
                   CASE 
                       WHEN c.client_type = 'legal' THEN c.company_name 
                       ELSE c.full_name 
                   END as client_name,
                   u.full_name as created_by_name
            FROM orders o
            LEFT JOIN clients c ON o.client_id = c.id
            LEFT JOIN users u ON o.created_by = u.id
            WHERE o.id = ?
        """, (order_id,))

        if not order_result:
            return None

        order = dict(order_result[0])

        services_result = self.execute_query("""
            SELECT os.*, s.name as service_name, s.description
            FROM order_services os
            LEFT JOIN services s ON os.service_id = s.id
            WHERE os.order_id = ?
        """, (order_id,))

        order['services'] = [dict(row) for row in services_result]
        return order

    def update_order_status(self, order_id: int, status: str) -> bool:
        try:
            query = "UPDATE orders SET status = ? WHERE id = ?"
            if status == 'completed':
                query = "UPDATE orders SET status = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?"

            rows_affected = self.execute_update(query, (status, order_id))
            return rows_affected > 0
        except sqlite3.Error as e:
            logger.error(f"Ошибка обновления статуса заказа: {e}")
            return False

    def get_report_data(self, date_from: str, date_to: str) -> List[Dict]:
        query = """
            SELECT 
                o.vessel_code,
                o.order_date,
                o.total_amount,
                o.status,
                CASE 
                    WHEN c.client_type = 'legal' THEN c.company_name 
                    ELSE c.full_name 
                END as client_name,
                c.client_type,
                c.inn,
                GROUP_CONCAT(s.name, ', ') as services_names,
                COUNT(DISTINCT os.service_id) as services_count
            FROM orders o
            LEFT JOIN clients c ON o.client_id = c.id
            LEFT JOIN order_services os ON o.id = os.order_id
            LEFT JOIN services s ON os.service_id = s.id
            WHERE o.order_date BETWEEN ? AND ?
            GROUP BY o.id
            ORDER BY o.order_date, o.vessel_code
        """
        result = self.execute_query(query, (date_from, date_to))
        return [dict(row) for row in result]


db_instance = Database()