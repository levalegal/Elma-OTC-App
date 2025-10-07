import hashlib
import logging
from typing import Optional, Dict, Any
from database import db_instance

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    pass


class AuthManager:
    def __init__(self):
        self.current_user: Optional[Dict] = None
        self._session_active = False

    def hash_password(self, password: str) -> str:
        """Используем тот же метод хеширования, что и в config"""
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, username: str, password: str) -> Dict[str, Any]:
        if not username or not password:
            raise AuthenticationError("Логин и пароль обязательны")

        if not db_instance.user_exists(username):
            raise AuthenticationError("Пользователь не найден")

        password_hash = self.hash_password(password)

        if not db_instance.verify_password(username, password_hash):
            raise AuthenticationError("Неверный пароль")

        user_info = db_instance.get_user_info(username)
        if not user_info:
            raise AuthenticationError("Ошибка получения данных пользователя")

        self.current_user = user_info
        self._session_active = True

        logger.info(f"Успешный вход пользователя: {username}")
        return user_info

    def logout(self) -> None:
        if self.current_user:
            logger.info(f"Выход пользователя: {self.current_user['username']}")
        self.current_user = None
        self._session_active = False

    def is_authenticated(self) -> bool:
        return self._session_active and self.current_user is not None

    def has_role(self, required_roles) -> bool:
        if not self.is_authenticated():
            return False

        if isinstance(required_roles, str):
            required_roles = [required_roles]

        return self.current_user['role'] in required_roles

    def get_user_permissions(self) -> Dict[str, bool]:
        if not self.is_authenticated():
            return {}

        role = self.current_user['role']

        permissions = {
            'can_create_orders': True,
            'can_view_orders': role in ['lab_assistant', 'controller'],
            'can_manage_orders': role in ['lab_assistant', 'controller'],
            'can_generate_reports': role in ['lab_assistant', 'controller'],
            'can_manage_clients': True,
            'can_manage_services': role == 'controller'
        }

        return permissions

    def get_current_user(self) -> Optional[Dict]:
        return self.current_user.copy() if self.current_user else None

    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        if len(password) < 6:
            return False, "Пароль должен содержать минимум 6 символов"

        if not any(c.isupper() for c in password):
            return False, "Пароль должен содержать хотя бы одну заглавную букву"

        if not any(c.isdigit() for c in password):
            return False, "Пароль должен содержать хотя бы одну цифру"

        return True, "Пароль соответствует требованиям"

    def change_password(self, current_password: str, new_password: str) -> bool:
        if not self.is_authenticated():
            raise AuthenticationError("Пользователь не аутентифицирован")

        username = self.current_user['username']
        current_hash = self.hash_password(current_password)

        if not db_instance.verify_password(username, current_hash):
            raise AuthenticationError("Текущий пароль неверен")

        is_valid, message = self.validate_password_strength(new_password)
        if not is_valid:
            raise AuthenticationError(message)

        new_hash = self.hash_password(new_password)

        try:
            query = "UPDATE users SET password_hash = ? WHERE username = ?"
            db_instance.execute_update(query, (new_hash, username))
            logger.info(f"Пароль изменен для пользователя: {username}")
            return True
        except Exception as e:
            logger.error(f"Ошибка изменения пароля: {e}")
            raise AuthenticationError("Ошибка изменения пароля")

    def get_available_roles(self) -> Dict[str, str]:
        return {
            'manager': 'Менеджер по работе с клиентами',
            'lab_assistant': 'Лаборант',
            'controller': 'Контроллер'
        }

    def get_role_display_name(self, role: str) -> str:
        roles = self.get_available_roles()
        return roles.get(role, role)


auth_manager = AuthManager()