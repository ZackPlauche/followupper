"""Message templates management widget."""

from .template_dialog import TemplateDialog
from ..models.message_template import MessageTemplate
from ..models.database import get_db
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QHeaderView, QMessageBox,
    QMenu, QAbstractItemView, QComboBox, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction


class TemplatesWidget(QWidget):
    """Widget for managing message templates."""

    template_updated = Signal()  # Signal emitted when templates are updated

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_templates()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Header with buttons and filter
        header_layout = QHBoxLayout()

        add_btn = QPushButton("Add Template")
        add_btn.clicked.connect(self.add_template)
        header_layout.addWidget(add_btn)

        edit_btn = QPushButton("Edit Template")
        edit_btn.clicked.connect(self.edit_template)
        header_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Delete Template")
        delete_btn.clicked.connect(self.delete_template)
        header_layout.addWidget(delete_btn)

        header_layout.addWidget(QLabel("Filter:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Email", "Codementor"])
        self.filter_combo.currentTextChanged.connect(self.load_templates)
        header_layout.addWidget(self.filter_combo)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_templates)
        header_layout.addWidget(refresh_btn)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Templates table
        self.templates_table = QTableWidget()
        self.templates_table.setColumnCount(5)
        self.templates_table.setHorizontalHeaderLabels([
            "Name", "Platform", "Subject", "Default", "Created"
        ])

        # Configure table
        self.templates_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.templates_table.setAlternatingRowColors(True)
        self.templates_table.setSortingEnabled(True)

        # Set column widths
        header = self.templates_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Platform
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Subject
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Default
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Created

        layout.addWidget(self.templates_table)

        # Context menu
        self.templates_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.templates_table.customContextMenuRequested.connect(self.show_context_menu)

    def load_templates(self):
        """Load templates from database and populate table."""
        try:
            db = next(get_db())

            # Apply filter
            filter_text = self.filter_combo.currentText()
            query = db.query(MessageTemplate).filter(MessageTemplate.is_active == True)

            if filter_text == "Email":
                query = query.filter(MessageTemplate.platform == "email")
            elif filter_text == "Codementor":
                query = query.filter(MessageTemplate.platform == "codementor")

            templates = query.all()

            self.templates_table.setRowCount(len(templates))

            for row, template in enumerate(templates):
                self.templates_table.setItem(row, 0, QTableWidgetItem(template.name or ""))
                self.templates_table.setItem(row, 1, QTableWidgetItem(template.platform or ""))
                self.templates_table.setItem(row, 2, QTableWidgetItem(template.subject or ""))
                self.templates_table.setItem(row, 3, QTableWidgetItem("Yes" if template.is_default else "No"))

                created = template.created_at.strftime("%Y-%m-%d") if template.created_at else "Unknown"
                self.templates_table.setItem(row, 4, QTableWidgetItem(created))

                # Store template ID in the row data
                self.templates_table.item(row, 0).setData(Qt.UserRole, template.id)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load templates: {str(e)}")

    def get_selected_template_id(self):
        """Get the ID of the currently selected template."""
        current_row = self.templates_table.currentRow()
        if current_row >= 0:
            item = self.templates_table.item(current_row, 0)
            if item:
                return item.data(Qt.UserRole)
        return None

    def get_selected_template(self):
        """Get the currently selected template from database."""
        template_id = self.get_selected_template_id()
        if not template_id:
            return None

        try:
            db = next(get_db())
            return db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
        except Exception:
            return None

    def add_template(self):
        """Add a new template."""
        dialog = TemplateDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_templates()
            self.template_updated.emit()

    def edit_template(self):
        """Edit the selected template."""
        template = self.get_selected_template()
        if not template:
            QMessageBox.warning(self, "No Selection", "Please select a template to edit.")
            return

        dialog = TemplateDialog(template=template, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_templates()
            self.template_updated.emit()

    def delete_template(self):
        """Delete the selected template."""
        template = self.get_selected_template()
        if not template:
            QMessageBox.warning(self, "No Selection", "Please select a template to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Delete Template",
            f"Are you sure you want to delete '{template.name}'?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                db = next(get_db())
                template.is_active = False  # Soft delete
                db.commit()
                self.load_templates()
                self.template_updated.emit()
                QMessageBox.information(self, "Success", "Template deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to delete template: {str(e)}")

    def show_context_menu(self, position):
        """Show context menu for the table."""
        if self.templates_table.itemAt(position) is None:
            return

        menu = QMenu(self)

        edit_action = QAction("Edit Template", self)
        edit_action.triggered.connect(self.edit_template)
        menu.addAction(edit_action)

        delete_action = QAction("Delete Template", self)
        delete_action.triggered.connect(self.delete_template)
        menu.addAction(delete_action)

        menu.exec(self.templates_table.mapToGlobal(position))
