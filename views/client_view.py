from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QComboBox, QRadioButton, QButtonGroup, QGroupBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
                             QDateEdit, QMessageBox, QTabWidget, QTextEdit, QDialog,
                             QFormLayout, QFrame, QSizePolicy, QScrollArea, QDialogButtonBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

from models.client import Client
from database import db_instance
from utils.helpers import helpers
from utils.validators import validators


class ClientDialog(QDialog):
    def __init__(self, client_type, parent=None):
        super().__init__(parent)
        self.client_type = client_type
        self.client_data = None
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setWindowTitle(f"Добавить {'юридическое' if self.client_type == 'legal' else 'физическое'} лицо")
        self.setMinimumSize(600, 700)
        self.setModal(True)

        layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        self.create_client_form(scroll_layout)

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.setMinimumHeight(40)
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.setMinimumHeight(40)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

    def create_client_form(self, layout):
        if self.client_type == 'legal':
            self.create_legal_form(layout)
        else:
            self.create_individual_form(layout)

    def create_legal_form(self, layout):
        company_group = QGroupBox("Информация о компании")
        company_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        company_form = QFormLayout()
        company_form.setVerticalSpacing(10)
        company_form.setHorizontalSpacing(15)

        self.company_name_edit = QLineEdit()
        self.company_name_edit.setPlaceholderText("ООО «Пример»")
        self.company_name_edit.setMinimumHeight(35)

        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("г. Санкт-Петербург, ул. Примерная, д. 1")
        self.address_edit.setMinimumHeight(35)

        self.inn_edit = QLineEdit()
        self.inn_edit.setPlaceholderText("1234567890")
        self.inn_edit.setMinimumHeight(35)

        self.bank_account_edit = QLineEdit()
        self.bank_account_edit.setPlaceholderText("40702810123456789012")
        self.bank_account_edit.setMinimumHeight(35)

        self.bik_edit = QLineEdit()
        self.bik_edit.setPlaceholderText("044525123")
        self.bik_edit.setMinimumHeight(35)

        company_form.addRow("Название компании *:", self.company_name_edit)
        company_form.addRow("Адрес:", self.address_edit)
        company_form.addRow("ИНН:", self.inn_edit)
        company_form.addRow("Расчетный счет:", self.bank_account_edit)
        company_form.addRow("БИК:", self.bik_edit)

        company_group.setLayout(company_form)
        layout.addWidget(company_group)

        contacts_group = QGroupBox("Контактная информация")
        contacts_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        contacts_form = QFormLayout()
        contacts_form.setVerticalSpacing(10)
        contacts_form.setHorizontalSpacing(15)

        self.director_name_edit = QLineEdit()
        self.director_name_edit.setPlaceholderText("Иванов Иван Иванович")
        self.director_name_edit.setMinimumHeight(35)

        self.contact_person_edit = QLineEdit()
        self.contact_person_edit.setPlaceholderText("Петров Петр Петрович")
        self.contact_person_edit.setMinimumHeight(35)

        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("+7 (912) 345-67-89")
        self.phone_edit.setMinimumHeight(35)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("example@company.ru")
        self.email_edit.setMinimumHeight(35)

        contacts_form.addRow("ФИО руководителя:", self.director_name_edit)
        contacts_form.addRow("Контактное лицо:", self.contact_person_edit)
        contacts_form.addRow("Телефон *:", self.phone_edit)
        contacts_form.addRow("Email:", self.email_edit)

        contacts_group.setLayout(contacts_form)
        layout.addWidget(contacts_group)

    def create_individual_form(self, layout):
        personal_group = QGroupBox("Персональная информация")
        personal_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        personal_form = QFormLayout()
        personal_form.setVerticalSpacing(10)
        personal_form.setHorizontalSpacing(15)

        self.full_name_edit = QLineEdit()
        self.full_name_edit.setPlaceholderText("Иванов Иван Иванович")
        self.full_name_edit.setMinimumHeight(35)

        self.birth_date_edit = QDateEdit()
        self.birth_date_edit.setDate(QDate(1980, 1, 1))
        self.birth_date_edit.setCalendarPopup(True)
        self.birth_date_edit.setMaximumDate(QDate.currentDate())
        self.birth_date_edit.setDisplayFormat("dd.MM.yyyy")
        self.birth_date_edit.setMinimumHeight(35)

        self.passport_series_edit = QLineEdit()
        self.passport_series_edit.setPlaceholderText("1234")
        self.passport_series_edit.setMinimumHeight(35)
        self.passport_series_edit.setMaxLength(4)

        self.passport_number_edit = QLineEdit()
        self.passport_number_edit.setPlaceholderText("567890")
        self.passport_number_edit.setMinimumHeight(35)
        self.passport_number_edit.setMaxLength(6)

        personal_form.addRow("ФИО *:", self.full_name_edit)
        personal_form.addRow("Дата рождения:", self.birth_date_edit)
        personal_form.addRow("Серия паспорта:", self.passport_series_edit)
        personal_form.addRow("Номер паспорта:", self.passport_number_edit)

        personal_group.setLayout(personal_form)
        layout.addWidget(personal_group)

        contacts_group = QGroupBox("Контактная информация")
        contacts_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        contacts_form = QFormLayout()
        contacts_form.setVerticalSpacing(10)
        contacts_form.setHorizontalSpacing(15)

        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("+7 (912) 345-67-89")
        self.phone_edit.setMinimumHeight(35)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("ivanov@mail.ru")
        self.email_edit.setMinimumHeight(35)

        contacts_form.addRow("Телефон *:", self.phone_edit)
        contacts_form.addRow("Email:", self.email_edit)

        contacts_group.setLayout(contacts_form)
        layout.addWidget(contacts_group)

    def setup_connections(self):
        self.save_btn.clicked.connect(self.on_save)
        self.cancel_btn.clicked.connect(self.reject)

    def on_save(self):
        client_data = self.get_form_data()
        client = Client.from_dict(client_data)

        is_valid, message = client.validate()
        if not is_valid:
            helpers.show_error(message, self)
            return

        try:
            self.client_data = client_data
            self.accept()
        except Exception as e:
            helpers.show_error(f"Ошибка сохранения: {e}", self)

    def get_form_data(self):
        data = {
            'client_type': self.client_type,
            'phone': self.phone_edit.text().strip()
        }

        if self.email_edit.text().strip():
            data['email'] = self.email_edit.text().strip()

        if self.client_type == 'legal':
            data.update({
                'company_name': self.company_name_edit.text().strip(),
                'address': self.address_edit.text().strip(),
                'inn': self.inn_edit.text().strip(),
                'bank_account': self.bank_account_edit.text().strip(),
                'bik': self.bik_edit.text().strip(),
                'director_name': self.director_name_edit.text().strip(),
                'contact_person': self.contact_person_edit.text().strip()
            })
        else:
            data.update({
                'full_name': self.full_name_edit.text().strip(),
                'birth_date': self.birth_date_edit.date().toString("yyyy-MM-dd"),
                'passport_series': self.passport_series_edit.text().strip(),
                'passport_number': self.passport_number_edit.text().strip()
            })

        return data

    def get_client_data(self):
        return self.client_data


class ClientTypeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.client_type = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Выбор типа клиента")
        self.setFixedSize(300, 200)
        self.setModal(True)

        layout = QVBoxLayout(self)

        label = QLabel("Выберите тип клиента:")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.legal_radio = QRadioButton("Юридическое лицо")
        self.individual_radio = QRadioButton("Физическое лицо")
        self.legal_radio.setChecked(True)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Отмена")

        ok_btn.clicked.connect(self.on_ok)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addWidget(label)
        layout.addWidget(self.legal_radio)
        layout.addWidget(self.individual_radio)
        layout.addStretch()
        layout.addLayout(button_layout)

    def on_ok(self):
        self.client_type = "legal" if self.legal_radio.isChecked() else "individual"
        self.accept()

    def get_client_type(self):
        return self.client_type


class ClientView(QWidget):
    def __init__(self):
        super().__init__()
        self.clients = []
        self.setup_ui()
        self.load_clients()
        self.setup_connections()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        controls_layout = QHBoxLayout()

        self.client_type_combo = QComboBox()
        self.client_type_combo.addItem("Все клиенты", "all")
        self.client_type_combo.addItem("Юридические лица", "legal")
        self.client_type_combo.addItem("Физические лица", "individual")
        self.client_type_combo.setMinimumHeight(35)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск по названию, ФИО, телефону...")
        self.search_edit.setMinimumHeight(35)

        self.add_client_btn = QPushButton("Добавить клиента")
        self.add_client_btn.setMinimumHeight(35)
        self.add_client_btn.setFixedWidth(150)

        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.setMinimumHeight(35)
        self.refresh_btn.setFixedWidth(100)

        controls_layout.addWidget(QLabel("Тип клиента:"))
        controls_layout.addWidget(self.client_type_combo)
        controls_layout.addWidget(self.search_edit, 1)
        controls_layout.addWidget(self.add_client_btn)
        controls_layout.addWidget(self.refresh_btn)

        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(6)
        self.clients_table.setHorizontalHeaderLabels([
            "ID", "Тип", "Название/ФИО", "Контакт", "Телефон", "Email"
        ])

        header = self.clients_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        self.clients_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.clients_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        layout.addLayout(controls_layout)
        layout.addWidget(self.clients_table)

    def load_clients(self):
        try:
            client_type = self.client_type_combo.currentData()
            if client_type == 'all':
                self.clients = db_instance.get_clients()
            else:
                self.clients = db_instance.get_clients(client_type)

            self.populate_clients_table()

        except Exception as e:
            helpers.show_error(f"Ошибка загрузки клиентов: {e}", self)

    def populate_clients_table(self):
        self.clients_table.setRowCount(len(self.clients))

        for row, client in enumerate(self.clients):
            self.clients_table.setItem(row, 0, QTableWidgetItem(str(client['id'])))

            client_type = "Юр. лицо" if client['client_type'] == 'legal' else "Физ. лицо"
            self.clients_table.setItem(row, 1, QTableWidgetItem(client_type))

            if client['client_type'] == 'legal':
                display_name = client['company_name'] or "Не указано"
                contact_info = client['contact_person'] or client['director_name'] or "Не указано"
            else:
                display_name = client['full_name'] or "Не указано"
                contact_info = f"Паспорт: {client['passport_series']} {client['passport_number']}" if client[
                    'passport_series'] else "Не указано"

            self.clients_table.setItem(row, 2, QTableWidgetItem(display_name))
            self.clients_table.setItem(row, 3, QTableWidgetItem(contact_info))
            self.clients_table.setItem(row, 4, QTableWidgetItem(client['phone'] or "Не указано"))
            self.clients_table.setItem(row, 5, QTableWidgetItem(client['email'] or "Не указано"))

    def setup_connections(self):
        self.client_type_combo.currentIndexChanged.connect(self.on_client_type_changed)
        self.search_edit.textChanged.connect(self.on_search)
        self.add_client_btn.clicked.connect(self.on_add_client)
        self.refresh_btn.clicked.connect(self.on_refresh)
        self.clients_table.cellDoubleClicked.connect(self.on_client_double_click)

    def on_client_type_changed(self):
        self.load_clients()

    def on_search(self, text):
        if not text.strip():
            self.load_clients()
            return

        try:
            client_type = self.client_type_combo.currentData()
            if client_type == 'all':
                search_results = db_instance.search_clients(text.strip())
            else:
                search_results = db_instance.search_clients(text.strip(), client_type)

            self.clients = search_results
            self.populate_clients_table()

        except Exception as e:
            helpers.show_error(f"Ошибка поиска: {e}", self)

    def on_add_client(self):
        dialog = ClientTypeDialog(self)
        if dialog.exec():
            client_type = dialog.get_client_type()
            client_dialog = ClientDialog(client_type, self)

            if client_dialog.exec():
                try:
                    client_data = client_dialog.get_client_data()
                    client_id = db_instance.create_client(client_data)
                    helpers.show_info("Клиент успешно добавлен", self)
                    self.load_clients()
                except Exception as e:
                    helpers.show_error(f"Ошибка добавления клиента: {e}", self)

    def on_refresh(self):
        self.load_clients()

    def on_client_double_click(self, row, column):
        client_id = int(self.clients_table.item(row, 0).text())
        client = next((c for c in self.clients if c['id'] == client_id), None)

        if client:
            self.show_client_details(client)

    def show_client_details(self, client):
        dialog = QDialog(self)
        dialog.setWindowTitle("Детали клиента")
        dialog.setMinimumSize(500, 400)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        self.create_client_details_view(scroll_layout, client)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setMinimumHeight(35)

        layout.addWidget(close_btn)

        dialog.exec()

    def create_client_details_view(self, layout, client):
        if client['client_type'] == 'legal':
            self.create_legal_details(layout, client)
        else:
            self.create_individual_details(layout, client)

    def create_legal_details(self, layout, client):
        groups = [
            ("Информация о компании", [
                ("Название компании", client['company_name']),
                ("Адрес", client['address']),
                ("ИНН", client['inn']),
                ("Расчетный счет", client['bank_account']),
                ("БИК", client['bik'])
            ]),
            ("Контактная информация", [
                ("ФИО руководителя", client['director_name']),
                ("Контактное лицо", client['contact_person']),
                ("Телефон", client['phone']),
                ("Email", client['email'])
            ])
        ]

        for group_title, fields in groups:
            group = QGroupBox(group_title)
            group_layout = QFormLayout()

            for field_name, field_value in fields:
                label = QLabel(field_name + ":")
                value = QLabel(field_value or "Не указано")
                value.setStyleSheet("font-weight: bold;")
                group_layout.addRow(label, value)

            group.setLayout(group_layout)
            layout.addWidget(group)

    def create_individual_details(self, layout, client):
        groups = [
            ("Персональная информация", [
                ("ФИО", client['full_name']),
                ("Дата рождения", helpers.format_date(client['birth_date']) if client['birth_date'] else "Не указано"),
                ("Паспорт", f"{client['passport_series']} {client['passport_number']}" if client[
                    'passport_series'] else "Не указано")
            ]),
            ("Контактная информация", [
                ("Телефон", client['phone']),
                ("Email", client['email'] or "Не указано")
            ])
        ]

        for group_title, fields in groups:
            group = QGroupBox(group_title)
            group_layout = QFormLayout()

            for field_name, field_value in fields:
                label = QLabel(field_name + ":")
                value = QLabel(field_value)
                value.setStyleSheet("font-weight: bold;")
                group_layout.addRow(label, value)

            group.setLayout(group_layout)
            layout.addWidget(group)

    def update_permissions(self, permissions):
        can_manage_clients = permissions.get('can_manage_clients', False)
        self.add_client_btn.setEnabled(can_manage_clients)

        if not can_manage_clients:
            self.add_client_btn.setToolTip("Недостаточно прав для управления клиентами")