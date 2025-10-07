from PyQt6.QtWidgets import (QTableView, QHeaderView, QAbstractItemView, QMenu,
                             QMessageBox, QStyledItemDelegate)
from PyQt6.QtCore import Qt, pyqtSignal, QModelIndex
from PyQt6.QtGui import QAction, QContextMenuEvent, QPainter, QColor


class CustomTableView(QTableView):
    rowDoubleClicked = pyqtSignal(int)
    contextMenuRequested = pyqtSignal(int, QModelIndex)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_table()
        self.setup_context_menu()

    def setup_table(self):
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setWordWrap(False)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        header.setSectionsClickable(True)

        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def setup_context_menu(self):
        self.context_menu = QMenu(self)

        self.view_details_action = QAction("Просмотреть детали", self)
        self.view_details_action.triggered.connect(self.on_view_details)

        self.edit_action = QAction("Редактировать", self)
        self.edit_action.triggered.connect(self.on_edit)

        self.delete_action = QAction("Удалить", self)
        self.delete_action.triggered.connect(self.on_delete)

        self.refresh_action = QAction("Обновить", self)
        self.refresh_action.triggered.connect(self.on_refresh)

        self.context_menu.addAction(self.view_details_action)
        self.context_menu.addAction(self.edit_action)
        self.context_menu.addSeparator()
        self.context_menu.addAction(self.delete_action)
        self.context_menu.addSeparator()
        self.context_menu.addAction(self.refresh_action)

    def contextMenuEvent(self, event: QContextMenuEvent):
        index = self.indexAt(event.pos())
        if index.isValid():
            row = index.row()
            self.contextMenuRequested.emit(row, index)
            self.context_menu.exec(event.globalPos())

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            index = self.indexAt(event.pos())
            if index.isValid():
                self.rowDoubleClicked.emit(index.row())
        super().mouseDoubleClickEvent(event)

    def on_view_details(self):
        current_index = self.currentIndex()
        if current_index.isValid():
            self.rowDoubleClicked.emit(current_index.row())

    def on_edit(self):
        current_index = self.currentIndex()
        if current_index.isValid():
            print(f"Редактирование строки {current_index.row()}")

    def on_delete(self):
        current_index = self.currentIndex()
        if current_index.isValid():
            reply = QMessageBox.question(
                self,
                "Подтверждение удаления",
                "Вы уверены, что хотите удалить выбранную запись?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                print(f"Удаление строки {current_index.row()}")

    def on_refresh(self):
        print("Обновление данных таблицы")

    def get_selected_row_id(self) -> int:
        current_index = self.currentIndex()
        if current_index.isValid():
            model = self.model()
            if model:
                return model.data(model.index(current_index.row(), 0))
        return -1

    def resize_columns_to_contents(self):
        self.resizeColumnsToContents()

    def set_column_hidden(self, column: int, hidden: bool):
        self.setColumnHidden(column, hidden)

    def set_column_width(self, column: int, width: int):
        self.setColumnWidth(column, width)

    def apply_styles(self):
        self.setStyleSheet("""
            CustomTableView {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                gridline-color: #e0e0e0;
            }
            CustomTableView::item {
                padding: 5px;
                border-bottom: 1px solid #f0f0f0;
            }
            CustomTableView::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                border-right: 1px solid #e0e0e0;
                border-bottom: 1px solid #e0e0e0;
                font-weight: bold;
            }
        """)