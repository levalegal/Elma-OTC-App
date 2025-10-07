import unittest
from decimal import Decimal
from datetime import datetime
from models.order import Order, OrderItem
from models.client import Client
from models.service import Service


class TestOrderItem(unittest.TestCase):
    def setUp(self):
        self.item = OrderItem(
            service_id=1,
            service_name="Тестовая услуга",
            description="Описание тестовой услуги",
            quantity=2,
            unit_price=Decimal('1000.00')
        )

    def test_total_price_calculation(self):
        expected_total = Decimal('2000.00')
        self.assertEqual(self.item.total_price, expected_total)

    def test_to_dict(self):
        item_dict = self.item.to_dict()

        self.assertEqual(item_dict['service_id'], 1)
        self.assertEqual(item_dict['service_name'], "Тестовая услуга")
        self.assertEqual(item_dict['quantity'], 2)
        self.assertEqual(item_dict['unit_price'], 1000.00)
        self.assertEqual(item_dict['total_price'], 2000.00)

    def test_quantity_validation(self):
        with self.assertRaises(TypeError):
            OrderItem(1, "Услуга", "Описание", "invalid", Decimal('100.00'))


class TestOrder(unittest.TestCase):
    def setUp(self):
        self.order = Order(
            id=1,
            vessel_code="VS000001",
            client_id=1,
            order_date="2024-01-01",
            total_amount=Decimal('5000.00'),
            status="new"
        )

    def test_add_item(self):
        self.order.add_item(1, "Услуга 1", "Описание 1", Decimal('1000.00'))
        self.assertEqual(len(self.order.items), 1)
        self.assertEqual(self.order.total_amount, Decimal('1000.00'))

    def test_add_duplicate_item(self):
        self.order.add_item(1, "Услуга 1", "Описание 1", Decimal('1000.00'), 2)
        self.order.add_item(1, "Услуга 1", "Описание 1", Decimal('1000.00'), 1)

        self.assertEqual(len(self.order.items), 1)
        self.assertEqual(self.order.items[0].quantity, 3)
        self.assertEqual(self.order.total_amount, Decimal('3000.00'))

    def test_remove_item(self):
        self.order.add_item(1, "Услуга 1", "Описание 1", Decimal('1000.00'))
        self.order.add_item(2, "Услуга 2", "Описание 2", Decimal('2000.00'))

        self.order.remove_item(1)

        self.assertEqual(len(self.order.items), 1)
        self.assertEqual(self.order.items[0].service_id, 2)
        self.assertEqual(self.order.total_amount, Decimal('2000.00'))

    def test_update_item_quantity(self):
        self.order.add_item(1, "Услуга 1", "Описание 1", Decimal('1000.00'), 2)
        self.order.update_item_quantity(1, 5)

        self.assertEqual(self.order.items[0].quantity, 5)
        self.assertEqual(self.order.total_amount, Decimal('5000.00'))

    def test_clear_items(self):
        self.order.add_item(1, "Услуга 1", "Описание 1", Decimal('1000.00'))
        self.order.clear_items()

        self.assertEqual(len(self.order.items), 0)
        self.assertEqual(self.order.total_amount, Decimal('0.00'))

    def test_status_display(self):
        self.assertEqual(self.order.status_display, "Новый")

        self.order.status = "completed"
        self.assertEqual(self.order.status_display, "Завершен")

    def test_items_count(self):
        self.order.add_item(1, "Услуга 1", "Описание 1", Decimal('1000.00'), 2)
        self.order.add_item(2, "Услуга 2", "Описание 2", Decimal('2000.00'), 1)

        self.assertEqual(self.order.items_count, 2)

    def test_can_edit(self):
        self.order.status = "new"
        self.assertTrue(self.order.can_edit)

        self.order.status = "completed"
        self.assertFalse(self.order.can_edit)

    def test_validation(self):
        order = Order()

        is_valid, message = order.validate()
        self.assertFalse(is_valid)
        self.assertIn("Код лабораторного сосуда обязателен", message)

        order.vessel_code = "VS000001"
        is_valid, message = order.validate()
        self.assertFalse(is_valid)
        self.assertIn("Клиент не выбран", message)

        order.client_id = 1
        is_valid, message = order.validate()
        self.assertFalse(is_valid)
        self.assertIn("Добавьте хотя бы одну услугу", message)


class TestClient(unittest.TestCase):
    def test_legal_client_creation(self):
        client = Client(
            client_type="legal",
            company_name="ООО «Тест»",
            inn="1234567890",
            phone="+79123456789"
        )

        is_valid, message = client.validate()
        self.assertTrue(is_valid)

    def test_individual_client_creation(self):
        client = Client(
            client_type="individual",
            full_name="Иванов Иван Иванович",
            phone="+79123456789"
        )

        is_valid, message = client.validate()
        self.assertTrue(is_valid)

    def test_client_validation(self):
        client = Client(client_type="legal")
        is_valid, message = client.validate()
        self.assertFalse(is_valid)
        self.assertIn("Название компании обязательно", message)

        client = Client(client_type="individual")
        is_valid, message = client.validate()
        self.assertFalse(is_valid)
        self.assertIn("ФИО обязательно", message)

    def test_display_name(self):
        legal_client = Client(client_type="legal", company_name="ООО «Тест»")
        self.assertEqual(legal_client.display_name, "ООО «Тест»")

        individual_client = Client(client_type="individual", full_name="Иванов И.И.")
        self.assertEqual(individual_client.display_name, "Иванов И.И.")

    def test_to_dict_legal(self):
        client = Client(
            client_type="legal",
            company_name="ООО «Тест»",
            inn="1234567890",
            phone="+79123456789"
        )

        client_dict = client.to_dict()
        self.assertEqual(client_dict['client_type'], 'legal')
        self.assertEqual(client_dict['company_name'], 'ООО «Тест»')
        self.assertEqual(client_dict['inn'], '1234567890')

    def test_to_dict_individual(self):
        client = Client(
            client_type="individual",
            full_name="Иванов Иван Иванович",
            phone="+79123456789"
        )

        client_dict = client.to_dict()
        self.assertEqual(client_dict['client_type'], 'individual')
        self.assertEqual(client_dict['full_name'], 'Иванов Иван Иванович')


class TestService(unittest.TestCase):
    def test_service_creation(self):
        service = Service(
            name="Тестовая услуга",
            description="Описание тестовой услуги",
            price=Decimal('1500.00')
        )

        is_valid, message = service.validate()
        self.assertTrue(is_valid)

    def test_service_validation(self):
        service = Service()
        is_valid, message = service.validate()
        self.assertFalse(is_valid)
        self.assertIn("Название услуги обязательно", message)

        service.name = "Тест"
        service.price = Decimal('0.00')
        is_valid, message = service.validate()
        self.assertFalse(is_valid)
        self.assertIn("Цена должна быть больше 0", message)

    def test_price_display(self):
        service = Service(price=Decimal('1234.56'))
        self.assertEqual(service.price_display, "1234.56 руб.")


if __name__ == '__main__':
    unittest.main()