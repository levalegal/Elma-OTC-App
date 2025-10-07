from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal

@dataclass
class OrderItem:
    service_id: int
    service_name: str
    description: str
    quantity: int = 1
    unit_price: Decimal = Decimal('0.00')

    @property
    def total_price(self) -> Decimal:
        return self.unit_price * self.quantity

    def to_dict(self) -> Dict[str, Any]:
        return {
            'service_id': self.service_id,
            'service_name': self.service_name,
            'description': self.description,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price)
        }

@dataclass
class Order:
    id: Optional[int] = None
    vessel_code: str = None
    client_id: int = None
    client_name: str = None
    order_date: str = None
    total_amount: Decimal = Decimal('0.00')
    status: str = 'new'
    created_by: int = None
    created_by_name: str = None
    created_at: str = None
    completed_at: str = None
    items: List[OrderItem] = field(default_factory=list)

    STATUS_CHOICES = {
        'new': 'Новый',
        'in_progress': 'В работе',
        'completed': 'Завершен',
        'cancelled': 'Отменен'
    }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Order':
        order = cls(
            id=data.get('id'),
            vessel_code=data.get('vessel_code'),
            client_id=data.get('client_id'),
            client_name=data.get('client_name'),
            order_date=data.get('order_date'),
            total_amount=Decimal(str(data.get('total_amount', '0.00'))),
            status=data.get('status', 'new'),
            created_by=data.get('created_by'),
            created_by_name=data.get('created_by_name'),
            created_at=data.get('created_at'),
            completed_at=data.get('completed_at')
        )

        if 'services' in data:
            for service_data in data['services']:
                item = OrderItem(
                    service_id=service_data['service_id'],
                    service_name=service_data.get('service_name', ''),
                    description=service_data.get('description', ''),
                    quantity=service_data.get('quantity', 1),
                    unit_price=Decimal(str(service_data.get('unit_price', '0.00')))
                )
                order.items.append(item)

        return order

    def to_dict(self) -> Dict[str, Any]:
        data = {
            'vessel_code': self.vessel_code,
            'client_id': self.client_id,
            'order_date': self.order_date or datetime.now().strftime('%Y-%m-%d'),
            'total_amount': float(self.total_amount),
            'status': self.status,
            'created_by': self.created_by
        }

        if self.id:
            data['id'] = self.id

        return data

    def add_item(self, service_id: int, service_name: str, description: str,
                 unit_price: Decimal, quantity: int = 1) -> None:
        for item in self.items:
            if item.service_id == service_id:
                item.quantity += quantity
                self._recalculate_total()
                return

        new_item = OrderItem(
            service_id=service_id,
            service_name=service_name,
            description=description,
            quantity=quantity,
            unit_price=unit_price
        )
        self.items.append(new_item)
        self._recalculate_total()

    def remove_item(self, service_id: int) -> None:
        self.items = [item for item in self.items if item.service_id != service_id]
        self._recalculate_total()

    def update_item_quantity(self, service_id: int, quantity: int) -> None:
        for item in self.items:
            if item.service_id == service_id:
                if quantity <= 0:
                    self.remove_item(service_id)
                else:
                    item.quantity = quantity
                break
        self._recalculate_total()

    def _recalculate_total(self) -> None:
        self.total_amount = sum(item.total_price for item in self.items)

    def clear_items(self) -> None:
        self.items.clear()
        self.total_amount = Decimal('0.00')

    @property
    def status_display(self) -> str:
        return self.STATUS_CHOICES.get(self.status, self.status)

    @property
    def items_count(self) -> int:
        return len(self.items)

    @property
    def can_edit(self) -> bool:
        return self.status in ['new', 'in_progress']

    @property
    def can_complete(self) -> bool:
        return self.status in ['new', 'in_progress'] and self.items_count > 0

    @property
    def can_cancel(self) -> bool:
        return self.status in ['new', 'in_progress']

    def validate(self) -> tuple[bool, str]:
        from utils.validators import validators

        if not self.vessel_code:
            return False, "Код лабораторного сосуда обязателен"

        is_valid, msg = validators.validate_vessel_code(self.vessel_code, check_unique=False)
        if not is_valid:
            return False, msg

        if not self.client_id:
            return False, "Клиент не выбран"

        if not self.items:
            return False, "Добавьте хотя бы одну услугу"

        if self.total_amount <= Decimal('0.00'):
            return False, "Сумма заказа должна быть больше 0"

        return True, "Валидация пройдена"