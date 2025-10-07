import unittest
from utils.validators import validators


class TestValidators(unittest.TestCase):
    def test_validate_inn(self):
        test_cases = [
            ("1234567890", True, ""),
            ("123456789012", True, ""),
            ("123456789", False, "10 или 12 цифр"),
            ("12345678901", False, "10 или 12 цифр"),
            ("123456789a", False, "только цифры"),
            ("", True, "")
        ]

        for inn, expected_valid, expected_message in test_cases:
            with self.subTest(inn=inn):
                is_valid, message = validators.validate_inn(inn)
                self.assertEqual(is_valid, expected_valid)
                if not expected_valid:
                    self.assertIn(expected_message, message)

    def test_validate_passport(self):
        test_cases = [
            ("1234", "567890", True, ""),
            ("123", "567890", False, "4 цифры"),
            ("1234", "56789", False, "6 цифр"),
            ("12a4", "567890", False, "только цифры"),
            ("", "", True, "")
        ]

        for series, number, expected_valid, expected_message in test_cases:
            with self.subTest(series=series, number=number):
                is_valid, message = validators.validate_passport(series, number)
                self.assertEqual(is_valid, expected_valid)
                if not expected_valid:
                    self.assertIn(expected_message, message)

    def test_validate_email(self):
        test_cases = [
            ("test@example.com", True, ""),
            ("test.name@example.co.uk", True, ""),
            ("invalid.email", False, "Неверный формат"),
            ("@example.com", False, "Неверный формат"),
            ("test@.com", False, "Неверный формат"),
            ("", True, "")
        ]

        for email, expected_valid, expected_message in test_cases:
            with self.subTest(email=email):
                is_valid, message = validators.validate_email(email)
                self.assertEqual(is_valid, expected_valid)
                if not expected_valid:
                    self.assertIn(expected_message, message)

    def test_validate_phone(self):
        test_cases = [
            ("79123456789", True, ""),
            ("89123456789", True, ""),
            ("+79123456789", True, ""),
            ("9123456789", True, ""),
            ("12345", False, "10 или 11 цифр"),
            ("7912345678a", False, "только цифры"),
            ("", False, "обязателен")
        ]

        for phone, expected_valid, expected_message in test_cases:
            with self.subTest(phone=phone):
                is_valid, message = validators.validate_phone(phone)
                self.assertEqual(is_valid, expected_valid)
                if not expected_valid:
                    self.assertIn(expected_message, message)

    def test_validate_date(self):
        test_cases = [
            ("2024-01-01", True, ""),
            ("2024-12-31", True, ""),
            ("2024-13-01", False, "Неверный формат"),
            ("01-01-2024", False, "Неверный формат"),
            ("", True, "")
        ]

        for date_str, expected_valid, expected_message in test_cases:
            with self.subTest(date_str=date_str):
                is_valid, message = validators.validate_date(date_str)
                self.assertEqual(is_valid, expected_valid)
                if not expected_valid:
                    self.assertIn(expected_message, message)

    def test_validate_bank_account(self):
        test_cases = [
            ("40702810123456789012", True, ""),
            ("4070281012345678901", False, "20 цифр"),
            ("407028101234567890123", False, "20 цифр"),
            ("4070281012345678901a", False, "только цифры"),
            ("", True, "")
        ]

        for account, expected_valid, expected_message in test_cases:
            with self.subTest(account=account):
                is_valid, message = validators.validate_bank_account(account)
                self.assertEqual(is_valid, expected_valid)
                if not expected_valid:
                    self.assertIn(expected_message, message)

    def test_validate_bik(self):
        test_cases = [
            ("044525123", True, ""),
            ("04452512", False, "9 цифр"),
            ("0445251234", False, "9 цифр"),
            ("04452512a", False, "только цифры"),
            ("", True, "")
        ]

        for bik, expected_valid, expected_message in test_cases:
            with self.subTest(bik=bik):
                is_valid, message = validators.validate_bik(bik)
                self.assertEqual(is_valid, expected_valid)
                if not expected_valid:
                    self.assertIn(expected_message, message)

    def test_validate_required_field(self):
        test_cases = [
            ("value", "Поле", True, ""),
            ("  value  ", "Поле", True, ""),
            ("", "Поле", False, "обязательно"),
            ("   ", "Поле", False, "обязательно"),
            (None, "Поле", False, "обязательно")
        ]

        for value, field_name, expected_valid, expected_message in test_cases:
            with self.subTest(value=value, field_name=field_name):
                is_valid, message = validators.validate_required_field(value, field_name)
                self.assertEqual(is_valid, expected_valid)
                if not expected_valid:
                    self.assertIn(expected_message, message)

    def test_validate_vessel_code(self):
        test_cases = [
            ("VS000001", True, ""),
            ("AB", False, "минимум 3 символа"),
            ("", False, "обязателен")
        ]

        for code, expected_valid, expected_message in test_cases:
            with self.subTest(code=code):
                is_valid, message = validators.validate_vessel_code(code, check_unique=False)
                self.assertEqual(is_valid, expected_valid)
                if not expected_valid:
                    self.assertIn(expected_message, message)


if __name__ == '__main__':
    unittest.main()