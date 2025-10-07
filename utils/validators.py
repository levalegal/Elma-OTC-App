import re
from datetime import datetime
from typing import Optional, Tuple


class Validators:
    @staticmethod
    def validate_inn(inn: str) -> Tuple[bool, str]:
        if not inn:
            return True, ""

        inn = inn.strip()

        if not inn.isdigit():
            return False, "ИНН должен содержать только цифры"

        if len(inn) not in [10, 12]:
            return False, "ИНН должен содержать 10 или 12 цифр"

        return True, ""

    @staticmethod
    def validate_passport(series: str, number: str) -> Tuple[bool, str]:
        if not series or not number:
            return True, ""

        series = series.strip()
        number = number.strip()

        if not series.isdigit() or len(series) != 4:
            return False, "Серия паспорта должна содержать 4 цифры"

        if not number.isdigit() or len(number) != 6:
            return False, "Номер паспорта должен содержать 6 цифр"

        return True, ""

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        if not email:
            return True, ""

        email = email.strip()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(pattern, email):
            return False, "Неверный формат email"

        return True, ""

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        if not phone:
            return False, "Телефон обязателен"

        phone = re.sub(r'[\s\-\(\)\+]', '', phone.strip())

        if not phone.isdigit():
            return False, "Телефон должен содержать только цифры"

        if len(phone) not in [10, 11]:
            return False, "Телефон должен содержать 10 или 11 цифр"

        return True, ""

    @staticmethod
    def validate_date(date_str: str) -> Tuple[bool, str]:
        if not date_str:
            return True, ""

        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True, ""
        except ValueError:
            return False, "Неверный формат даты. Используйте ГГГГ-ММ-ДД"

    @staticmethod
    def validate_bank_account(account: str) -> Tuple[bool, str]:
        if not account:
            return True, ""

        account = account.strip()

        if not account.isdigit():
            return False, "Расчетный счет должен содержать только цифры"

        if len(account) != 20:
            return False, "Расчетный счет должен содержать 20 цифр"

        return True, ""

    @staticmethod
    def validate_bik(bik: str) -> Tuple[bool, str]:
        if not bik:
            return True, ""

        bik = bik.strip()

        if not bik.isdigit():
            return False, "БИК должен содержать только цифры"

        if len(bik) != 9:
            return False, "БИК должен содержать 9 цифр"

        return True, ""

    @staticmethod
    def validate_required_field(value: str, field_name: str) -> Tuple[bool, str]:
        if not value or not value.strip():
            return False, f"Поле '{field_name}' обязательно для заполнения"
        return True, ""

    @staticmethod
    def validate_vessel_code(code: str, check_unique: bool = True) -> Tuple[bool, str]:
        from database import db_instance

        if not code or not code.strip():
            return False, "Код лабораторного сосуда обязателен"

        code = code.strip()

        if len(code) < 3:
            return False, "Код должен содержать минимум 3 символа"

        if check_unique and db_instance.vessel_code_exists(code):
            return False, "Код сосуда уже существует"

        return True, ""


validators = Validators()