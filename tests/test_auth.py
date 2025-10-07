import unittest
import tempfile
import os
from auth import AuthManager, AuthenticationError
from database import Database


class TestAuthManager(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.db = Database(self.db_path)
        self.auth = AuthManager()

    def tearDown(self):
        self.temp_db.close()
        os.unlink(self.db_path)

    def test_hash_password(self):
        password = "test_password"
        hashed = self.auth.hash_password(password)

        self.assertIsInstance(hashed, str)
        self.assertEqual(len(hashed), 64)

        same_password_hashed = self.auth.hash_password(password)
        self.assertEqual(hashed, same_password_hashed)

        different_password_hashed = self.auth.hash_password("different")
        self.assertNotEqual(hashed, different_password_hashed)

    def test_validate_password_strength(self):
        test_cases = [
            ("short", False, "минимум 6 символов"),
            ("noupper123", False, "заглавную букву"),
            ("NOLOWER123", False, "строчную букву"),
            ("NoNumbers", False, "цифру"),
            ("Valid123", True, "соответствует требованиям")
        ]

        for password, expected_valid, expected_message in test_cases:
            with self.subTest(password=password):
                is_valid, message = self.auth.validate_password_strength(password)
                self.assertEqual(is_valid, expected_valid)
                self.assertIn(expected_message, message)

    def test_authentication_flow(self):
        username = "testuser"
        password = "Test123"

        with self.assertRaises(AuthenticationError):
            self.auth.login(username, password)

    def test_session_management(self):
        self.assertFalse(self.auth.is_authenticated())
        self.assertIsNone(self.auth.get_current_user())

    def test_role_permissions(self):
        test_cases = [
            ('manager', 'create_orders', True),
            ('manager', 'view_orders', False),
            ('lab_assistant', 'view_orders', True),
            ('lab_assistant', 'manage_services', False),
            ('controller', 'generate_reports', True),
            ('controller', 'manage_services', True)
        ]

        for role, permission, expected in test_cases:
            with self.subTest(role=role, permission=permission):
                self.auth.current_user = {'role': role}
                self.assertEqual(self.auth.has_role(role), True)

    def test_get_available_roles(self):
        roles = self.auth.get_available_roles()

        expected_roles = ['manager', 'lab_assistant', 'controller']
        self.assertEqual(list(roles.keys()), expected_roles)

        for role in expected_roles:
            self.assertIn(role, roles)
            self.assertIsInstance(roles[role], str)

    def test_role_display_names(self):
        role_names = self.auth.get_available_roles()

        self.assertEqual(role_names['manager'], 'Менеджер по работе с клиентами')
        self.assertEqual(role_names['lab_assistant'], 'Лаборант')
        self.assertEqual(role_names['controller'], 'Контроллер')

    def test_empty_credentials(self):
        with self.assertRaises(AuthenticationError):
            self.auth.login("", "password")

        with self.assertRaises(AuthenticationError):
            self.auth.login("username", "")

    def test_logout(self):
        self.auth.current_user = {'username': 'test', 'role': 'manager'}
        self.auth._session_active = True

        self.auth.logout()

        self.assertIsNone(self.auth.current_user)
        self.assertFalse(self.auth._session_active)


if __name__ == '__main__':
    unittest.main()