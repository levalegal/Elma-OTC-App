import csv
import os
from datetime import datetime
from typing import List, Dict

# Проверка доступности reportlab
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import mm

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class DataExporter:
    @staticmethod
    def export_to_csv(data: List[Dict], filename: str, delimiter: str = ';') -> bool:
        try:
            if not data:
                return False

            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = list(data[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=delimiter)
                writer.writeheader()

                for row in data:
                    writer.writerow(row)

            return True
        except Exception as e:
            print(f"Ошибка экспорта в CSV: {e}")
            return False

    @staticmethod
    def export_to_pdf(data: List[Dict], filename: str, title: str = "Отчет") -> bool:
        if not REPORTLAB_AVAILABLE:
            print("PDF экспорт недоступен: не установлен reportlab")
            return False

        try:
            if not data:
                return False

            doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                rightMargin=20 * mm,
                leftMargin=20 * mm,
                topMargin=20 * mm,
                bottomMargin=20 * mm
            )

            elements = []
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1
            )

            elements.append(Paragraph(title, title_style))
            elements.append(Spacer(1, 10))

            table_data = []
            if data:
                headers = list(data[0].keys())
                header_row = [DataExporter._format_header(header) for header in headers]
                table_data.append(header_row)

                for row in data:
                    table_row = [str(row.get(header, '')) for header in headers]
                    table_data.append(table_row)

            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 20))

            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=2
            )

            timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            footer_text = f"Сгенерировано: {timestamp} | Всего записей: {len(data)}"
            elements.append(Paragraph(footer_text, footer_style))

            doc.build(elements)
            return True

        except Exception as e:
            print(f"Ошибка экспорта в PDF: {e}")
            return False

    @staticmethod
    def _format_header(header: str) -> str:
        header_map = {
            'id': 'ID',
            'vessel_code': 'Код сосуда',
            'order_date': 'Дата заказа',
            'total_amount': 'Сумма',
            'status': 'Статус',
            'client_name': 'Клиент',
            'client_type': 'Тип клиента',
            'inn': 'ИНН',
            'services_names': 'Услуги',
            'services_count': 'Кол-во услуг',
            'company_name': 'Название компании',
            'full_name': 'ФИО',
            'phone': 'Телефон',
            'email': 'Email',
            'address': 'Адрес',
            'created_at': 'Дата создания'
        }
        return header_map.get(header, header)

    @staticmethod
    def export_orders_report(orders_data: List[Dict], filename: str, date_from: str, date_to: str) -> bool:
        if not REPORTLAB_AVAILABLE:
            print("PDF экспорт недоступен: не установлен reportlab")
            return False

        try:
            doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                rightMargin=15 * mm,
                leftMargin=15 * mm,
                topMargin=15 * mm,
                bottomMargin=15 * mm
            )

            elements = []
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                'ReportTitle',
                parent=styles['Heading1'],
                fontSize=14,
                spaceAfter=20,
                alignment=1
            )

            report_title = f"Отчет по заказам ОТК\nпериод с {date_from} по {date_to}"
            elements.append(Paragraph(report_title, title_style))

            if orders_data:
                table_data = []
                headers = ['vessel_code', 'order_date', 'client_name', 'services_names', 'total_amount', 'status']
                header_row = [DataExporter._format_header(header) for header in headers]
                table_data.append(header_row)

                for order in orders_data:
                    table_row = [
                        order.get('vessel_code', ''),
                        order.get('order_date', ''),
                        order.get('client_name', ''),
                        order.get('services_names', ''),
                        f"{order.get('total_amount', 0):.2f} руб.",
                        DataExporter._format_status(order.get('status', ''))
                    ]
                    table_data.append(table_row)

                table = Table(table_data, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))

                elements.append(Spacer(1, 15))
                elements.append(table)

            timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=2
            )
            elements.append(Spacer(1, 20))
            elements.append(Paragraph(f"Отчет сгенерирован: {timestamp}", footer_style))

            doc.build(elements)
            return True

        except Exception as e:
            print(f"Ошибка генерации отчета: {e}")
            return False

    @staticmethod
    def _format_status(status: str) -> str:
        status_map = {
            'new': 'Новый',
            'in_progress': 'В работе',
            'completed': 'Завершен',
            'cancelled': 'Отменен'
        }
        return status_map.get(status, status)


data_exporter = DataExporter()