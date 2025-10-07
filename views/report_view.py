from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QComboBox, QDateEdit, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView, QGroupBox, QFormLayout, QFrame,
                             QProgressBar, QMessageBox, QFileDialog, QTabWidget, QTextEdit)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta

from database import db_instance
from auth import auth_manager
from utils.helpers import helpers
from utils.exporters import data_exporter


class ReportView(QWidget):
    def __init__(self):
        super().__init__()
        self.report_data = []
        self.setup_ui()
        self.setup_connections()
        self.set_default_dates()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        controls_group = self.create_controls_group()
        main_layout.addWidget(controls_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        results_group = self.create_results_group()
        main_layout.addWidget(results_group)

        actions_group = self.create_actions_group()
        main_layout.addWidget(actions_group)

    def create_controls_group(self):
        group = QGroupBox("Параметры отчета")
        group.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        layout = QFormLayout()
        layout.setVerticalSpacing(10)
        layout.setHorizontalSpacing(15)

        date_layout = QHBoxLayout()

        self.date_from_edit = QDateEdit()
        self.date_from_edit.setCalendarPopup(True)
        self.date_from_edit.setDisplayFormat("dd.MM.yyyy")
        self.date_from_edit.setMinimumHeight(35)

        self.date_to_edit = QDateEdit()
        self.date_to_edit.setCalendarPopup(True)
        self.date_to_edit.setDisplayFormat("dd.MM.yyyy")
        self.date_to_edit.setMinimumHeight(35)

        date_layout.addWidget(QLabel("с:"))
        date_layout.addWidget(self.date_from_edit)
        date_layout.addWidget(QLabel("по:"))
        date_layout.addWidget(self.date_to_edit)
        date_layout.addStretch()

        status_layout = QHBoxLayout()
        self.status_combo = QComboBox()
        self.status_combo.addItem("Все статусы", "all")
        self.status_combo.addItem("Новые", "new")
        self.status_combo.addItem("В работе", "in_progress")
        self.status_combo.addItem("Завершенные", "completed")
        self.status_combo.addItem("Отмененные", "cancelled")
        self.status_combo.setMinimumHeight(35)

        status_layout.addWidget(QLabel("Статус заказа:"))
        status_layout.addWidget(self.status_combo)
        status_layout.addStretch()

        self.generate_btn = QPushButton("Сформировать отчет")
        self.generate_btn.setMinimumHeight(40)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        quick_filters_layout = QHBoxLayout()
        today_btn = QPushButton("Сегодня")
        week_btn = QPushButton("Неделя")
        month_btn = QPushButton("Месяц")
        quarter_btn = QPushButton("Квартал")
        year_btn = QPushButton("Год")

        for btn in [today_btn, week_btn, month_btn, quarter_btn, year_btn]:
            btn.setMinimumHeight(30)
            btn.setFixedWidth(80)
            btn.clicked.connect(lambda checked, b=btn: self.on_quick_filter(b.text()))

        quick_filters_layout.addWidget(QLabel("Быстрые периоды:"))
        quick_filters_layout.addWidget(today_btn)
        quick_filters_layout.addWidget(week_btn)
        quick_filters_layout.addWidget(month_btn)
        quick_filters_layout.addWidget(quarter_btn)
        quick_filters_layout.addWidget(year_btn)
        quick_filters_layout.addStretch()

        layout.addRow("Период:", date_layout)
        layout.addRow(quick_filters_layout)
        layout.addRow("", status_layout)
        layout.addRow("", self.generate_btn)

        group.setLayout(layout)
        return group

    def create_results_group(self):
        group = QGroupBox("Результаты отчета")
        group.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        layout = QVBoxLayout()

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels([
            "Код сосуда", "Дата заказа", "Клиент", "Тип клиента",
            "Услуги", "Сумма", "Статус", "ИНН"
        ])

        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)

        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.results_table.setAlternatingRowColors(True)

        layout.addWidget(self.results_table)
        group.setLayout(layout)
        return group

    def create_actions_group(self):
        group = QGroupBox("Действия с отчетом")
        group.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        layout = QHBoxLayout()

        self.export_csv_btn = QPushButton("Экспорт в CSV")
        self.export_pdf_btn = QPushButton("Экспорт в PDF")
        self.export_excel_btn = QPushButton("Экспорт в Excel")
        self.clear_btn = QPushButton("Очистить")

        for btn in [self.export_csv_btn, self.export_pdf_btn, self.export_excel_btn, self.clear_btn]:
            btn.setMinimumHeight(35)
            btn.setFixedWidth(120)

        layout.addWidget(self.export_csv_btn)
        layout.addWidget(self.export_pdf_btn)
        layout.addWidget(self.export_excel_btn)
        layout.addStretch()
        layout.addWidget(self.clear_btn)

        group.setLayout(layout)
        return group

    def set_default_dates(self):
        end_date = QDate.currentDate()
        start_date = end_date.addMonths(-1)

        self.date_from_edit.setDate(start_date)
        self.date_to_edit.setDate(end_date)

    def setup_connections(self):
        self.generate_btn.clicked.connect(self.on_generate_report)
        self.export_csv_btn.clicked.connect(self.on_export_csv)
        self.export_pdf_btn.clicked.connect(self.on_export_pdf)
        self.export_excel_btn.clicked.connect(self.on_export_excel)
        self.clear_btn.clicked.connect(self.on_clear)

    def on_quick_filter(self, period):
        end_date = QDate.currentDate()

        if period == "Сегодня":
            start_date = end_date
        elif period == "Неделя":
            start_date = end_date.addDays(-7)
        elif period == "Месяц":
            start_date = end_date.addMonths(-1)
        elif period == "Квартал":
            start_date = end_date.addMonths(-3)
        elif period == "Год":
            start_date = end_date.addYears(-1)
        else:
            start_date = end_date.addMonths(-1)

        self.date_from_edit.setDate(start_date)
        self.date_to_edit.setDate(end_date)

    def on_generate_report(self):
        date_from = self.date_from_edit.date().toString("yyyy-MM-dd")
        date_to = self.date_to_edit.date().toString("yyyy-MM-dd")
        status = self.status_combo.currentData()

        if date_from > date_to:
            helpers.show_error("Дата 'с' не может быть больше даты 'по'", self)
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        QTimer.singleShot(100, lambda: self.generate_report_data(date_from, date_to, status))

    def generate_report_data(self, date_from, date_to, status):
        try:
            filters = {
                'date_from': date_from,
                'date_to': date_to
            }

            if status != 'all':
                filters['status'] = status

            self.report_data = db_instance.get_report_data(date_from, date_to)

            if status != 'all':
                self.report_data = [row for row in self.report_data if row['status'] == status]

            self.populate_results_table()

            helpers.show_info(
                f"Отчет сформирован\n"
                f"Период: {helpers.format_date(date_from)} - {helpers.format_date(date_to)}\n"
                f"Найдено записей: {len(self.report_data)}",
                self
            )

        except Exception as e:
            helpers.show_error(f"Ошибка формирования отчета: {e}", self)

        finally:
            self.progress_bar.setVisible(False)

    def populate_results_table(self):
        self.results_table.setRowCount(len(self.report_data))

        for row, data in enumerate(self.report_data):
            self.results_table.setItem(row, 0, QTableWidgetItem(data['vessel_code']))
            self.results_table.setItem(row, 1, QTableWidgetItem(helpers.format_date(data['order_date'])))
            self.results_table.setItem(row, 2, QTableWidgetItem(data['client_name']))

            client_type = "Юр. лицо" if data['client_type'] == 'legal' else "Физ. лицо"
            self.results_table.setItem(row, 3, QTableWidgetItem(client_type))

            self.results_table.setItem(row, 4, QTableWidgetItem(data['services_names'] or ""))

            amount_item = QTableWidgetItem(f"{float(data['total_amount']):.2f} руб.")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.results_table.setItem(row, 5, amount_item)

            status_display = self.get_status_display(data['status'])
            status_item = QTableWidgetItem(status_display)

            status_color = self.get_status_color(data['status'])
            status_item.setBackground(status_color)

            self.results_table.setItem(row, 6, status_item)
            self.results_table.setItem(row, 7, QTableWidgetItem(data['inn'] or ""))

    def get_status_display(self, status):
        status_map = {
            'new': 'Новый',
            'in_progress': 'В работе',
            'completed': 'Завершен',
            'cancelled': 'Отменен'
        }
        return status_map.get(status, status)

    def get_status_color(self, status):
        from PyQt6.QtGui import QColor

        color_map = {
            'new': QColor(255, 255, 200),
            'in_progress': QColor(200, 230, 255),
            'completed': QColor(200, 255, 200),
            'cancelled': QColor(255, 200, 200)
        }
        return color_map.get(status, QColor(255, 255, 255))

    def on_export_csv(self):
        if not self.report_data:
            helpers.show_warning("Нет данных для экспорта", self)
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт в CSV",
            f"otk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )

        if filename:
            success = data_exporter.export_to_csv(self.report_data, filename)
            if success:
                helpers.show_info(f"Отчет успешно экспортирован в {filename}", self)
            else:
                helpers.show_error("Ошибка экспорта в CSV", self)

    def on_export_pdf(self):
        if not self.report_data:
            helpers.show_warning("Нет данных для экспорта", self)
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт в PDF",
            f"otk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf)"
        )

        if filename:
            date_from = self.date_from_edit.date().toString("yyyy-MM-dd")
            date_to = self.date_to_edit.date().toString("yyyy-MM-dd")

            success = data_exporter.export_orders_report(self.report_data, filename, date_from, date_to)
            if success:
                helpers.show_info(f"Отчет успешно экспортирован в {filename}", self)
            else:
                helpers.show_error("Ошибка экспорта в PDF", self)

    def on_export_excel(self):
        helpers.show_info("Экспорт в Excel будет реализован в следующей версии", self)

    def on_clear(self):
        self.report_data.clear()
        self.results_table.setRowCount(0)
        self.set_default_dates()
        self.status_combo.setCurrentIndex(0)

    def update_permissions(self, permissions):
        can_generate_reports = permissions.get('can_generate_reports', False)

        self.generate_btn.setEnabled(can_generate_reports)
        self.export_csv_btn.setEnabled(can_generate_reports)
        self.export_pdf_btn.setEnabled(can_generate_reports)
        self.export_excel_btn.setEnabled(can_generate_reports)

        if not can_generate_reports:
            tooltip = "Недостаточно прав для генерации отчетов"
            self.generate_btn.setToolTip(tooltip)
            self.export_csv_btn.setToolTip(tooltip)
            self.export_pdf_btn.setToolTip(tooltip)
            self.export_excel_btn.setToolTip(tooltip)