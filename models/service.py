from dataclasses import dataclass
from typing import Dict, Any, Optional
from decimal import Decimal


@dataclass
class Service:
    id: Optional[int] = None
    name: str = None
    description: str = None
    price: Decimal = Decimal('0.00')
    is_active: bool = True
    created_at: str = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Service':
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description'),
            price=Decimal(str(data.get('price', '0.00'))),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        data = {
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'is_active': self.is_active
        }

        if self.id:
            data['id'] = self.id
        if self.created_at:
            data['created_at'] = self.created_at

        return data

    def validate(self) -> tuple[bool, str]:
        if not self.name or not self.name.strip():
            return False, "Название услуги обязательно"

        if len(self.name.strip()) < 3:
            return False, "Название услуги должно содержать минимум 3 символа"

        if self.price <= Decimal('0.00'):
            return False, "Цена должна быть больше 0"

        return True, "Валидация пройдена"

    @property
    def price_display(self) -> str:
        return f"{self.price:.2f} руб."