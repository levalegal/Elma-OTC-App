from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class Client:
    id: Optional[int] = None
    client_type: str = None
    company_name: Optional[str] = None
    address: Optional[str] = None
    inn: Optional[str] = None
    bank_account: Optional[str] = None
    bik: Optional[str] = None
    director_name: Optional[str] = None
    contact_person: Optional[str] = None
    full_name: Optional[str] = None
    birth_date: Optional[str] = None
    passport_series: Optional[str] = None
    passport_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Client':
        return cls(
            id=data.get('id'),
            client_type=data.get('client_type'),
            company_name=data.get('company_name'),
            address=data.get('address'),
            inn=data.get('inn'),
            bank_account=data.get('bank_account'),
            bik=data.get('bik'),
            director_name=data.get('director_name'),
            contact_person=data.get('contact_person'),
            full_name=data.get('full_name'),
            birth_date=data.get('birth_date'),
            passport_series=data.get('passport_series'),
            passport_number=data.get('passport_number'),
            phone=data.get('phone'),
            email=data.get('email'),
            created_at=data.get('created_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        data = {
            'client_type': self.client_type,
            'phone': self.phone,
            'email': self.email
        }

        if self.id:
            data['id'] = self.id

        if self.client_type == 'legal':
            data.update({
                'company_name': self.company_name,
                'address': self.address,
                'inn': self.inn,
                'bank_account': self.bank_account,
                'bik': self.bik,
                'director_name': self.director_name,
                'contact_person': self.contact_person
            })
        else:
            data.update({
                'full_name': self.full_name,
                'birth_date': self.birth_date,
                'passport_series': self.passport_series,
                'passport_number': self.passport_number
            })

        if self.created_at:
            data['created_at'] = self.created_at

        return data

    @property
    def display_name(self) -> str:
        if self.client_type == 'legal':
            return self.company_name or 'Неизвестная компания'
        else:
            return self.full_name or 'Неизвестный клиент'

    @property
    def contact_info(self) -> str:
        info = []
        if self.phone:
            info.append(f"тел: {self.phone}")
        if self.email:
            info.append(f"email: {self.email}")
        return ", ".join(info)

    def validate(self) -> tuple[bool, str]:
        from utils.validators import validators

        if not self.client_type:
            return False, "Тип клиента не указан"

        if not self.phone:
            return False, "Телефон обязателен"

        is_valid, msg = validators.validate_phone(self.phone)
        if not is_valid:
            return False, msg

        if self.email:
            is_valid, msg = validators.validate_email(self.email)
            if not is_valid:
                return False, msg

        if self.client_type == 'legal':
            if not self.company_name:
                return False, "Название компании обязательно"

            if self.inn:
                is_valid, msg = validators.validate_inn(self.inn)
                if not is_valid:
                    return False, msg

            if self.bank_account:
                is_valid, msg = validators.validate_bank_account(self.bank_account)
                if not is_valid:
                    return False, msg

            if self.bik:
                is_valid, msg = validators.validate_bik(self.bik)
                if not is_valid:
                    return False, msg

        else:
            if not self.full_name:
                return False, "ФИО обязательно"

            if self.passport_series or self.passport_number:
                is_valid, msg = validators.validate_passport(
                    self.passport_series, self.passport_number
                )
                if not is_valid:
                    return False, msg

        return True, "Валидация пройдена"