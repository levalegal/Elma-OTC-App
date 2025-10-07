from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class User:
    id: int
    username: str
    role: str
    full_name: str
    is_active: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            role=data.get('role'),
            full_name=data.get('full_name'),
            is_active=data.get('is_active', True)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'full_name': self.full_name,
            'is_active': self.is_active
        }

    @property
    def role_display(self) -> str:
        role_names = {
            'manager': 'Менеджер по работе с клиентами',
            'lab_assistant': 'Лаборант',
            'controller': 'Контроллер'
        }
        return role_names.get(self.role, self.role)

    def has_permission(self, permission: str) -> bool:
        permissions = {
            'create_orders': True,
            'view_orders': self.role in ['lab_assistant', 'controller'],
            'manage_orders': self.role in ['lab_assistant', 'controller'],
            'generate_reports': self.role in ['lab_assistant', 'controller'],
            'manage_clients': True,
            'manage_services': self.role == 'controller'
        }
        return permissions.get(permission, False)