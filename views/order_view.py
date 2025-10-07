from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QComboBox, QRadioButton, QButtonGroup, QGroupBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
                             QDateEdit, QSpinBox, QDoubleSpinBox, QMessageBox, QScrollArea,
                             QFormLayout, QFrame, QSizePolicy, QTabWidget, QTextEdit)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime

from models.order import Order, OrderItem
from models.client import Client
from database import db_instance
from auth import auth_manager
from utils.helpers import helpers
from utils.validators import validators


class OrderView(QWidget):
    order_created = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.current_order = Order()
        self.available_services = []
        self.clients = []
        self.setup_ui()
        self.load_initial_data()
        self.setup_connections()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)

        order_info_group = self.create_order_info_group()
        client_selection_group = self.create_client_selection_group()
        services_group = self.create_services_group()

        left_layout.addWidget(order_info_group)
        left_layout.addWidget(client_selection_group)
        left_layout.addWidget(services_group)
        left_layout.setStretchFactor(services_group, 1)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)

        order_summary_group = self.create_order_summary_group()
        actions_group = self.create_actions_group()

        right_layout.addWidget(order_summary_group)
        right_layout.addWidget(actions_group)
        right_layout.setStretchFactor(order_summary_group, 1)

        main_layout.addLayout(left_layout, 3)
        main_layout.addLayout(right_layout, 1)

    def create_order_info_group(self):
        group = QGroupBox("Информация о заказе")
        group.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        layout = QFormLayout()
        layout.setVerticalSpacing(10)
        layout.setHorizontalSpacing(15)

        self.vessel_code_edit = QLineEdit()
        self.vessel_code_edit.setPlaceholderText("Автоматически генерируется")
        self.vessel_code_edit.setReadOnly(True)
        self.vessel_code_edit.setMinimumHeight(35)

        self.order_date_edit = QDateEdit()
        self.order_date_edit.setDate(QDate.currentDate())
        self.order_date_edit.setCalendarPopup(True)
        self.order_date_edit.setMinimumHeight(35)
        self.order_date_edit.setDisplayFormat("dd.MM.yyyy")

        layout.addRow("Код лабораторного сосуда:", self.vessel_code_edit)
        layout.addRow("Дата заказа:", self.order_date_edit)

        group.setLayout(layout)
        return group

    def create_client_selection_group(self):
        group = QGroupBox("Выбор заказчика")
        group.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        layout = QVBoxLayout()
        layout.setSpacing(10)

        client_type_layout = QHBoxLayout()
        self.legal_radio = QRadioButton("Юридическое лицо")
        self.individual_radio = QRadioButton("Физическое лицо")

        self.client_type_group = QButtonGroup()
        self.client_type_group.addButton(self.legal_radio)
        self.client_type_group.addButton(self.individual_radio)

        client_type_layout.addWidget(self.legal_radio)
        client_type_layout.addWidget(self.individual_radio)
        client_type_layout.addStretch()

        self.client_search_layout = QHBoxLayout()
        self.client_combo = QComboBox()
        self.client_combo.setEditable(True)
        self.client_combo.setMinimumHeight(35)
        self.client_combo.setPlaceholderText("Начните вводить название или ФИО...")

        self.add_client_btn = QPushButton("Добавить")
        self.add_client_btn.setMinimumHeight(35)
        self.add_client_btn.setFixedWidth(100)

        self.client_search_layout.addWidget(self.client_combo)
        self.client_search_layout.addWidget(self.add_client_btn)

        self.client_info_frame = QFrame()
        self.client_info_frame.setVisible(False)
        self.client_info_frame.setFrameShape(QFrame.Shape.Box)
        self.client_info_layout = QVBoxLayout(self.client_info_frame)

        self.client_name_label = QLabel()
        self.client_contact_label = QLabel()

        self.client_info_layout.addWidget(self.client_name_label)
        self.client_info_layout.addWidget(self.client_contact_label)

        layout.addLayout(client_type_layout)
        layout.addLayout(self.client_search_layout)
        layout.addWidget(self.client_info_frame)

        group.setLayout(layout)
        return group

    def create_services_group(self):
        group = QGroupBox("Услуги и исследования")
        group.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        layout = QVBoxLayout()
        layout.setSpacing(10)

        services_selection_layout = QHBoxLayout()
        self.services_combo = QComboBox()
        self.services_combo.setMinimumHeight(35)

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(100)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setFixedWidth(80)

        self.add_service_btn = QPushButton("Добавить")
        self.add_service_btn.setMinimumHeight(35)
        self.add_service_btn.setFixedWidth(100)

        services_selection_layout.addWidget(QLabel("Услуга:"))
        services_selection_layout.addWidget(self.services_combo, 1)
        services_selection_layout.addWidget(QLabel("Кол-во:"))
        services_selection_layout.addWidget(self.quantity_spin)
        services_selection_layout.addWidget(self.add_service_btn)

        self.services_table = QTableWidget()
        self.services_table.setColumnCount(5)
        self.services_table.setHorizontalHeaderLabels(["Услуга", "Описание", "Цена", "Кол-во", "Сумма"])
        self.services_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.services_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.services_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        header = self.services_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        layout.addLayout(services_selection_layout)
        layout.addWidget(self.services_table)

        group.setLayout(layout)
        return group

    def create_order_summary_group(self):
        group = QGroupBox("Сводка заказа")
        group.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        layout = QVBoxLayout()
        layout.setSpacing(10)

        summary_frame = QFrame()
        summary_frame.setFrameShape(QFrame.Shape.Box)
        summary_layout = QVBoxLayout(summary_frame)

        self.summary_labels = {}
        fields = [
            ("vessel_code", "Код сосуда:"),
            ("order_date", "Дата заказа:"),
            ("client_name", "Клиент:"),
            ("services_count", "Кол-во услуг:"),
            ("total_amount", "Общая сумма:")
        ]

        for field, label_text in fields:
            row_layout = QHBoxLayout()
            label = QLabel(label_text)
            value_label = QLabel("-")
            value_label.setObjectName(f"summary_{field}")
            value_label.setStyleSheet("font-weight: bold; color: #2c3e50;")

            row_layout.addWidget(label)
            row_layout.addWidget(value_label)
            row_layout.addStretch()

            summary_layout.addLayout(row_layout)
            self.summary_labels[field] = value_label

        summary_layout.addStretch()
        layout.addWidget(summary_frame)

        group.setLayout(layout)
        return group

    def create_actions_group(self):
        group = QGroupBox("Действия")
        group.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        layout = QVBoxLayout()
        layout.setSpacing(10)

        self.create_order_btn = QPushButton("Создать заказ")
        self.create_order_btn.setMinimumHeight(45)
        self.create_order_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)

        self.clear_form_btn = QPushButton("Очистить форму")
        self.clear_form_btn.setMinimumHeight(35)

        layout.addWidget(self.create_order_btn)
        layout.addWidget(self.clear_form_btn)
        layout.addStretch()

        group.setLayout(layout)
        return group

    def load_initial_data(self):
        self.available_services = db_instance.get_services()
        self.populate_services_combo()
        self.generate_vessel_code()

    def populate_services_combo(self):
        self.services_combo.clear()
        for service in self.available_services:
            price = service['price']
            display_text = f"{service['name']} - {price:.2f} руб."
            self.services_combo.addItem(display_text, service['id'])

    def generate_vessel_code(self):
        next_code = helpers.get_next_vessel_code()
        self.vessel_code_edit.setText(next_code)
        self.current_order.vessel_code = next_code

    def setup_connections(self):
        self.client_type_group.buttonClicked.connect(self.on_client_type_changed)
        self.add_client_btn.clicked.connect(self.on_add_client)
        self.add_service_btn.clicked.connect(self.on_add_service)
        self.create_order_btn.clicked.connect(self.on_create_order)
        self.clear_form_btn.clicked.connect(self.on_clear_form)

        self.client_combo.currentIndexChanged.connect(self.on_client_selected)
        self.services_table.cellDoubleClicked.connect(self.on_remove_service)

    def on_client_type_changed(self):
        client_type = "legal" if self.legal_radio.isChecked() else "individual"
        self.load_clients(client_type)
        self.client_combo.setCurrentIndex(-1)
        self.client_info_frame.setVisible(False)
        self.current_order.client_id = None

    def load_clients(self, client_type):
        self.clients = db_instance.get_clients(client_type)
        self.client_combo.clear()

        for client in self.clients:
            display_name = client['company_name'] if client_type == 'legal' else client['full_name']
            self.client_combo.addItem(display_name, client['id'])

    def on_client_selected(self, index):
        if index >= 0:
            client_id = self.client_combo.currentData()
            self.set_client_info(client_id)

    def on_add_client(self):
        from views.client_view import ClientDialog

        client_type = "legal" if self.legal_radio.isChecked() else "individual"
        dialog = ClientDialog(client_type, self)

        if dialog.exec():
            new_client = dialog.get_client_data()
            try:
                client_id = db_instance.create_client(new_client)
                self.load_clients(client_type)
                self.client_combo.setCurrentIndex(self.client_combo.findData(client_id))
                helpers.show_info("Клиент успешно добавлен", self)
            except Exception as e:
                helpers.show_error(f"Ошибка добавления клиента: {e}", self)

    def on_add_service(self):
        current_index = self.services_combo.currentIndex()
        if current_index < 0:
            helpers.show_warning("Выберите услугу", self)
            return

        service_id = self.services_combo.currentData()
        quantity = self.quantity_spin.value()

        service_data = next((s for s in self.available_services if s['id'] == service_id), None)
        if not service_data:
            return

        self.current_order.add_item(
            service_id,
            service_data['name'],
            service_data['description'],
            service_data['price'],
            quantity
        )

        self.update_services_table()
        self.update_order_summary()

    def on_remove_service(self, row, column):
        service_id = self.current_order.items[row].service_id
        self.current_order.remove_item(service_id)
        self.update_services_table()
        self.update_order_summary()

    def update_services_table(self):
        self.services_table.setRowCount(len(self.current_order.items))

        for row, item in enumerate(self.current_order.items):
            self.services_table.setItem(row, 0, QTableWidgetItem(item.service_name))
            self.services_table.setItem(row, 1, QTableWidgetItem(item.description))
            self.services_table.setItem(row, 2, QTableWidgetItem(f"{item.unit_price:.2f} руб."))
            self.services_table.setItem(row, 3, QTableWidgetItem(str(item.quantity)))
            self.services_table.setItem(row, 4, QTableWidgetItem(f"{item.total_price:.2f} руб."))

    def update_order_summary(self):
        self.summary_labels['vessel_code'].setText(self.current_order.vessel_code or "-")
        self.summary_labels['order_date'].setText(
            helpers.format_date(self.order_date_edit.date().toString("yyyy-MM-dd"))
        )
        self.summary_labels['services_count'].setText(str(self.current_order.items_count))
        self.summary_labels['total_amount'].setText(
            helpers.format_currency(self.current_order.total_amount)
        )

    def on_create_order(self):
        if not self.validate_form():
            return

        try:
            order_data = {
                'vessel_code': self.current_order.vessel_code,
                'client_id': self.current_order.client_id,
                'order_date': self.order_date_edit.date().toString("yyyy-MM-dd"),
                'total_amount': float(self.current_order.total_amount),
                'created_by': auth_manager.get_current_user()['id']
            }

            services_data = []
            for item in self.current_order.items:
                services_data.append({
                    'service_id': item.service_id,
                    'unit_price': float(item.unit_price),
                    'quantity': item.quantity
                })

            order_id = db_instance.create_order(order_data, services_data)

            helpers.show_info(
                f"Заказ успешно создан!\nНомер заказа: {order_id}",
                self
            )

            self.order_created.emit()
            self.on_clear_form()

        except Exception as e:
            helpers.show_error(f"Ошибка создания заказа: {e}", self)

    def validate_form(self):
        if not self.current_order.vessel_code:
            helpers.show_error("Код сосуда не указан", self)
            return False

        if not self.current_order.client_id:
            helpers.show_error("Клиент не выбран", self)
            return False

        if self.current_order.items_count == 0:
            helpers.show_error("Добавьте хотя бы одну услугу", self)
            return False

        return True

    def on_clear_form(self):
        self.current_order = Order()
        self.generate_vessel_code()
        self.order_date_edit.setDate(QDate.currentDate())
        self.client_combo.setCurrentIndex(-1)
        self.client_info_frame.setVisible(False)
        self.services_table.setRowCount(0)
        self.update_order_summary()

    def set_client_info(self, client_id):
        client_type = "legal" if self.legal_radio.isChecked() else "individual"
        client = next((c for c in self.clients if c['id'] == client_id), None)

        if client:
            self.current_order.client_id = client_id

            if client_type == 'legal':
                display_name = client['company_name']
                contact_info = f"Тел: {client['phone']}"
                if client['email']:
                    contact_info += f", Email: {client['email']}"
            else:
                display_name = client['full_name']
                contact_info = f"Тел: {client['phone']}"
                if client['email']:
                    contact_info += f", Email: {client['email']}"

            self.client_name_label.setText(display_name)
            self.client_contact_label.setText(contact_info)
            self.client_info_frame.setVisible(True)

            self.summary_labels['client_name'].setText(display_name)

    def update_permissions(self, permissions):
        can_create_orders = permissions.get('can_create_orders', False)
        self.create_order_btn.setEnabled(can_create_orders)

        if not can_create_orders:
            self.create_order_btn.setToolTip("Недостаточно прав для создания заказов")