import os
import csv
from datetime import datetime, date
from typing import Any, Dict, List
from decimal import Decimal
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt6.QtCore import QDate


class Helpers:
    @staticmethod
    def show_message(title: str, message: str, icon=QMessageBox.Icon.Information, parent=None):
        msg = QMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(icon)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        return msg.exec()

    @staticmethod
    def show_error(message: str, parent=None):
        return Helpers.show_message("Ошибка", message, QMessageBox.Icon.Critical, parent)

    @staticmethod
    def show_warning(message: str, parent=None):
        return Helpers.show_message("Предупреждение", message, QMessageBox.Icon.Warning, parent)

    @staticmethod
    def show_info(message: str, parent=None):
        return Helpers.show_message("Информация", message, QMessageBox.Icon.Information, parent)

    @staticmethod
    def confirm_action(title: str, message: str, parent=None) -> bool:
        reply = QMessageBox.question(
            parent,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    @staticmethod
    def format_date(date_str: str, input_format: str = '%Y-%m-%d', output_format: str = '%d.%m.%Y') -> str:
        try:
            date_obj = datetime.strptime(date_str, input_format)
            return date_obj.strftime(output_format)
        except (ValueError, TypeError):
            return date_str

    @staticmethod
    def parse_date(date_str: str, format: str = '%Y-%m-%d') -> datetime:
        try:
            return datetime.strptime(date_str, format)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def qdate_to_str(qdate: QDate, format: str = 'yyyy-MM-dd') -> str:
        return qdate.toString(format)

    @staticmethod
    def str_to_qdate(date_str: str, format: str = 'yyyy-MM-dd') -> QDate:
        return QDate.fromString(date_str, format)

    @staticmethod
    def format_currency(amount: Decimal) -> str:
        return f"{amount:,.2f} руб.".replace(',', ' ').replace('.', ',')

    @staticmethod
    def parse_currency(currency_str: str) -> Decimal:
        try:
            cleaned = currency_str.replace(' руб.', '').replace(' ', '').replace(',', '.')
            return Decimal(cleaned)
        except:
            return Decimal('0.00')

    @staticmethod
    def validate_decimal(value: str) -> tuple[bool, Decimal]:
        try:
            decimal_value = Decimal(value.replace(',', '.'))
            return True, decimal_value
        except:
            return False, Decimal('0.00')

    @staticmethod
    def export_to_csv(data: List[Dict], filename: str, headers: Dict[str, str] = None):
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if not data:
                    return False

                fieldnames = list(data[0].keys())
                if headers:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow(headers)
                else:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()

                for row in data:
                    writer.writerow(row)

            return True
        except Exception as e:
            print(f"Ошибка экспорта в CSV: {e}")
            return False

    @staticmethod
    def create_table_item(value: Any) -> QTableWidgetItem:
        if value is None:
            item = QTableWidgetItem("")
        elif isinstance(value, (int, float, Decimal)):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        elif isinstance(value, bool):
            item = QTableWidgetItem("Да" if value else "Нет")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        elif isinstance(value, (datetime, date)):
            formatted = Helpers.format_date(str(value))
            item = QTableWidgetItem(formatted)
        else:
            item = QTableWidgetItem(str(value))

        return item

    @staticmethod
    def get_next_vessel_code() -> str:
        from database import db_instance
        last_id = db_instance.get_last_order_id()
        return f"VS{last_id + 1:06d}"

    @staticmethod
    def format_phone(phone: str) -> str:
        if not phone:
            return ""

        digits = ''.join(filter(str.isdigit, phone))

        if len(digits) == 10:
            return f"+7 ({digits[0:3]}) {digits[3:6]}-{digits[6:8]}-{digits[8:10]}"
        elif len(digits) == 11:
            return f"+{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
        else:
            return phone


helpers = Helpers()