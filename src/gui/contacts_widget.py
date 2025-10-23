"""Modern contacts widget with inline editing and reactive UI."""

from ..models.contact import Contact
from ..models.database import get_db
from .contact_dialog import ContactDialog
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QHeaderView, QFrame, QScrollArea,
    QMessageBox, QAbstractItemView, QComboBox, QStyledItemDelegate
)
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor, QPalette, QPainter, QPen
from datetime import datetime, timezone


class InlineEditDelegate(QStyledItemDelegate):
    """Delegate for inline editing in table cells."""

    def createEditor(self, parent, option, index):
        """Create appropriate editor for different columns."""
        if index.column() == 1:  # Email column
            editor = QLineEdit(parent)
            editor.setPlaceholderText("Enter email address")
            return editor
        elif index.column() == 2:  # Codementor column
            editor = QLineEdit(parent)
            editor.setPlaceholderText("Enter Codementor username")
            return editor
        elif index.column() == 3:  # Platform column
            editor = QComboBox(parent)
            editor.addItems(["email", "codementor", "both"])
            return editor
        elif index.column() == 5:  # Notes column
            editor = QLineEdit(parent)
            editor.setPlaceholderText("Enter notes")
            return editor
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        """Set editor data from model."""
        value = index.model().data(index, Qt.EditRole)
        if isinstance(editor, QLineEdit):
            editor.setText(str(value) if value else "")
        elif isinstance(editor, QComboBox):
            editor.setCurrentText(str(value) if value else "email")

    def setModelData(self, editor, model, index):
        """Set model data from editor."""
        if isinstance(editor, QLineEdit):
            model.setData(index, editor.text(), Qt.EditRole)
        elif isinstance(editor, QComboBox):
            model.setData(index, editor.currentText(), Qt.EditRole)


class ModernTableWidget(QTableWidget):
    """Modern styled table widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modernTable")
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setShowGrid(False)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Set modern styling
        self.setStyleSheet("""
            QTableWidget#modernTable {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                gridline-color: #f1f5f9;
                selection-background-color: #667eea;
                selection-color: white;
                font-size: 14px;
            }

            QTableWidget#modernTable::item {
                padding: 12px 16px;
                border-bottom: 1px solid #f1f5f9;
            }

            QTableWidget#modernTable::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
            }

            QTableWidget#modernTable::item:hover {
                background: #f8fafc;
            }

            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f8fafc, stop:1 #e2e8f0);
                color: #4a5568;
                font-weight: 600;
                font-size: 13px;
                padding: 16px;
                border: none;
                border-right: 1px solid #e2e8f0;
                border-bottom: 2px solid #667eea;
            }

            QScrollBar:vertical {
                background: #f1f5f9;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #cbd5e0;
                border-radius: 6px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background: #a0aec0;
            }
        """)


class ContactsWidget(QWidget):
    """Modern contacts management widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.contacts = []
        self.setup_ui()
        self.load_contacts()

    def setup_ui(self):
        """Set up the modern user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Header section
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Title and subtitle
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)

        title = QLabel("👥 Contacts")
        title.setObjectName("sectionTitle")
        title.setStyleSheet("""
            QLabel#sectionTitle {
                font-size: 28px;
                font-weight: 700;
                color: #1a202c;
                margin: 0px;
            }
        """)

        subtitle = QLabel("Manage your contacts and follow-up sequences")
        subtitle.setObjectName("sectionSubtitle")
        subtitle.setStyleSheet("""
            QLabel#sectionSubtitle {
                font-size: 16px;
                color: #718096;
                margin: 0px;
            }
        """)

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)

        # Add stretch to push buttons to the right
        header_layout.addStretch()

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        self.add_button = QPushButton("➕ Add Contact")
        self.add_button.setObjectName("primaryButton")
        self.add_button.clicked.connect(self.add_contact)

        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setObjectName("secondaryButton")
        self.refresh_button.clicked.connect(self.refresh)

        self.export_button = QPushButton("📤 Export")
        self.export_button.setObjectName("secondaryButton")
        self.export_button.clicked.connect(self.export_contacts)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.export_button)
        header_layout.addLayout(button_layout)

        layout.addWidget(header_frame)

        # Search bar
        search_frame = QFrame()
        search_frame.setObjectName("searchFrame")
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)

        search_label = QLabel("🔍 Search:")
        search_label.setStyleSheet("font-weight: 600; color: #4a5568;")

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search contacts by name, email, or notes...")
        self.search_edit.setObjectName("searchInput")
        self.search_edit.textChanged.connect(self.filter_contacts)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        layout.addWidget(search_frame)

        # Contacts table
        self.contacts_table = ModernTableWidget()
        self.setup_table()
        layout.addWidget(self.contacts_table)

        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setStyleSheet("""
            QLabel#statusLabel {
                color: #718096;
                font-size: 12px;
                padding: 8px 0px;
            }
        """)
        layout.addWidget(self.status_label)

        # Apply button styling
        self.apply_button_styling()

    def apply_button_styling(self):
        """Apply modern button styling."""
        self.setStyleSheet("""
            QPushButton#primaryButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
                min-height: 20px;
            }

            QPushButton#primaryButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a6fd8, stop:1 #6a4190);
            }

            QPushButton#primaryButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4c63d2, stop:1 #5e3a7e);
            }

            QPushButton#secondaryButton {
                background: white;
                color: #4a5568;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 14px;
                min-height: 20px;
            }

            QPushButton#secondaryButton:hover {
                background: #f8fafc;
                border-color: #cbd5e0;
            }

            QPushButton#secondaryButton:pressed {
                background: #edf2f7;
            }

            QLineEdit#searchInput {
                background: white;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: #4a5568;
            }

            QLineEdit#searchInput:focus {
                border-color: #667eea;
                background: #f8fafc;
            }

            QFrame#headerFrame, QFrame#searchFrame {
                background: transparent;
            }
        """)

    def setup_table(self):
        """Set up the contacts table."""
        # Set column headers
        headers = ["ID", "Name", "Email", "Codementor", "Platform", "Notes", "Status", "Actions"]
        self.contacts_table.setColumnCount(len(headers))
        self.contacts_table.setHorizontalHeaderLabels(headers)

        # Set column widths
        header = self.contacts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Email
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # Codementor
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Platform
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Notes
        header.setSectionResizeMode(6, QHeaderView.Fixed)  # Status
        header.setSectionResizeMode(7, QHeaderView.Fixed)  # Actions

        self.contacts_table.setColumnWidth(0, 60)   # ID
        self.contacts_table.setColumnWidth(3, 120)  # Codementor
        self.contacts_table.setColumnWidth(4, 100)  # Platform
        self.contacts_table.setColumnWidth(6, 80)   # Status
        self.contacts_table.setColumnWidth(7, 100)  # Actions

        # Set delegate for inline editing
        delegate = InlineEditDelegate()
        self.contacts_table.setItemDelegate(delegate)

        # Connect signals
        self.contacts_table.itemChanged.connect(self.on_item_changed)
        self.contacts_table.cellDoubleClicked.connect(self.on_cell_double_clicked)

    def load_contacts(self):
        """Load contacts from database."""
        try:
            db = next(get_db())
            self.contacts = db.query(Contact).order_by(Contact.name).all()
            self.populate_table()
            self.update_status(f"Loaded {len(self.contacts)} contacts")
        except Exception as e:
            self.update_status(f"Error loading contacts: {str(e)}")
            QMessageBox.critical(self, "Database Error", f"Failed to load contacts: {str(e)}")

    def populate_table(self):
        """Populate the table with contact data."""
        self.contacts_table.setRowCount(len(self.contacts))

        for row, contact in enumerate(self.contacts):
            # ID
            id_item = QTableWidgetItem(str(contact.id))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.contacts_table.setItem(row, 0, id_item)

            # Name
            name_item = QTableWidgetItem(contact.name or "")
            self.contacts_table.setItem(row, 1, name_item)

            # Email
            email_item = QTableWidgetItem(contact.email or "")
            self.contacts_table.setItem(row, 2, email_item)

            # Codementor
            codementor_item = QTableWidgetItem(contact.codementor_username or "")
            self.contacts_table.setItem(row, 3, codementor_item)

            # Platform
            platform_item = QTableWidgetItem(contact.platform_preference or "email")
            self.contacts_table.setItem(row, 4, platform_item)

            # Notes
            notes_item = QTableWidgetItem(contact.notes or "")
            self.contacts_table.setItem(row, 5, notes_item)

            # Status
            status_item = QTableWidgetItem("🟢 Active" if contact.is_active else "🔴 Inactive")
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            self.contacts_table.setItem(row, 6, status_item)

            # Actions
            actions_item = QTableWidgetItem("✏️ Edit | 🗑️ Delete")
            actions_item.setFlags(actions_item.flags() & ~Qt.ItemIsEditable)
            self.contacts_table.setItem(row, 7, actions_item)

    def filter_contacts(self):
        """Filter contacts based on search text."""
        search_text = self.search_edit.text().lower()
        if not search_text:
            self.populate_table()
            return

        filtered_contacts = []
        for contact in self.contacts:
            if (search_text in (contact.name or "").lower() or
                search_text in (contact.email or "").lower() or
                    search_text in (contact.notes or "").lower()):
                filtered_contacts.append(contact)

        # Temporarily replace contacts list
        original_contacts = self.contacts
        self.contacts = filtered_contacts
        self.populate_table()
        self.contacts = original_contacts

    def on_item_changed(self, item):
        """Handle item changes for inline editing."""
        row = item.row()
        column = item.column()

        if row < len(self.contacts):
            contact = self.contacts[row]

            try:
                db = next(get_db())

                if column == 1:  # Name
                    contact.name = item.text()
                elif column == 2:  # Email
                    contact.email = item.text() if item.text() else None
                elif column == 3:  # Codementor
                    contact.codementor_username = item.text() if item.text() else None
                elif column == 4:  # Platform
                    contact.platform_preference = item.text()
                elif column == 5:  # Notes
                    contact.notes = item.text() if item.text() else None

                contact.updated_at = datetime.now(timezone.utc)
                db.commit()

                self.update_status(f"Updated contact: {contact.name}")

            except Exception as e:
                QMessageBox.critical(self, "Update Error", f"Failed to update contact: {str(e)}")
                # Reload to revert changes
                self.load_contacts()

    def on_cell_double_clicked(self, row, column):
        """Handle double-click for editing."""
        if column == 7:  # Actions column
            self.edit_contact(row)
        else:
            # Enable editing for the clicked cell
            self.contacts_table.editItem(self.contacts_table.item(row, column))

    def add_contact(self):
        """Add a new contact."""
        dialog = ContactDialog(parent=self)
        if dialog.exec() == dialog.Accepted:
            self.load_contacts()
            self.update_status("Contact added successfully")

    def edit_contact(self, row):
        """Edit an existing contact."""
        if row < len(self.contacts):
            contact = self.contacts[row]
            dialog = ContactDialog(contact=contact, parent=self)
            if dialog.exec() == dialog.Accepted:
                self.load_contacts()
                self.update_status(f"Updated contact: {contact.name}")

    def delete_contact(self, row):
        """Delete a contact."""
        if row < len(self.contacts):
            contact = self.contacts[row]

            reply = QMessageBox.question(
                self, 'Delete Contact',
                f'Are you sure you want to delete "{contact.name}"?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                try:
                    db = next(get_db())
                    db.delete(contact)
                    db.commit()
                    self.load_contacts()
                    self.update_status(f"Deleted contact: {contact.name}")
                except Exception as e:
                    QMessageBox.critical(self, "Delete Error", f"Failed to delete contact: {str(e)}")

    def export_contacts(self):
        """Export contacts to CSV."""
        # This would be implemented to export contacts
        self.update_status("Export functionality coming soon!")

    def refresh(self):
        """Refresh the contacts list."""
        self.load_contacts()

    def update_status(self, message):
        """Update the status label."""
        self.status_label.setText(f"📊 {message}")
