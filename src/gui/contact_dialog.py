"""Modern contact management dialog."""

from ..models.contact import Contact
from ..models.database import get_db
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QPushButton,
    QDialogButtonBox, QMessageBox, QLabel, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from datetime import datetime, timezone


class ContactDialog(QDialog):
    """Modern dialog for adding/editing contacts."""

    def __init__(self, contact=None, parent=None):
        super().__init__(parent)
        self.contact = contact
        self.setWindowTitle("Add Contact" if not contact else "Edit Contact")
        self.setModal(True)
        self.setFixedSize(600, 500)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.setup_ui()
        if contact:
            self.load_contact_data()

    def setup_ui(self):
        """Set up the modern user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # Header
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        title = QLabel("👤 Contact Details")
        title.setObjectName("dialogTitle")
        title.setStyleSheet("""
            QLabel#dialogTitle {
                font-size: 24px;
                font-weight: 700;
                color: #1a202c;
                margin: 0px;
            }
        """)

        subtitle = QLabel("Enter the contact information below")
        subtitle.setObjectName("dialogSubtitle")
        subtitle.setStyleSheet("""
            QLabel#dialogSubtitle {
                font-size: 14px;
                color: #718096;
                margin: 0px;
            }
        """)

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addWidget(header_frame)

        # Form
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Name field
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter contact name")
        self.name_edit.setObjectName("formInput")
        form_layout.addRow("Name *:", self.name_edit)

        # Email field
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Enter email address")
        self.email_edit.setObjectName("formInput")
        form_layout.addRow("Email:", self.email_edit)

        # Codementor username
        self.codementor_edit = QLineEdit()
        self.codementor_edit.setPlaceholderText("Enter Codementor username")
        self.codementor_edit.setObjectName("formInput")
        form_layout.addRow("Codementor:", self.codementor_edit)

        # Platform preference
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["email", "codementor", "both"])
        self.platform_combo.setObjectName("formCombo")
        form_layout.addRow("Platform:", self.platform_combo)

        # Follow-up sequences info
        sequences_label = QLabel("Follow-up sequences will be managed separately")
        sequences_label.setObjectName("infoLabel")
        sequences_label.setStyleSheet("""
            QLabel#infoLabel {
                color: #718096;
                font-style: italic;
                font-size: 12px;
                padding: 8px 12px;
                background: #f8fafc;
                border-radius: 6px;
                border-left: 3px solid #667eea;
            }
        """)
        form_layout.addRow("Sequences:", sequences_label)

        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Enter any notes about this contact")
        self.notes_edit.setMaximumHeight(100)
        self.notes_edit.setObjectName("formTextArea")
        form_layout.addRow("Notes:", self.notes_edit)

        layout.addWidget(form_frame)

        # Buttons
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(12)

        self.save_button = QPushButton("💾 Save Contact")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.save_contact)

        self.cancel_button = QPushButton("❌ Cancel")
        self.cancel_button.setObjectName("secondaryButton")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addWidget(button_frame)

        # Apply styling
        self.apply_styling()

    def apply_styling(self):
        """Apply modern styling to the dialog."""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8fafc, stop:1 #e2e8f0);
            }

            QFrame#headerFrame, QFrame#formFrame, QFrame {
                background: transparent;
            }

            QLineEdit#formInput {
                background: white;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: #4a5568;
                min-height: 20px;
            }

            QLineEdit#formInput:focus {
                border-color: #667eea;
                background: #f8fafc;
            }

            QComboBox#formCombo {
                background: white;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: #4a5568;
                min-height: 20px;
            }

            QComboBox#formCombo:focus {
                border-color: #667eea;
                background: #f8fafc;
            }

            QComboBox#formCombo::drop-down {
                border: none;
                width: 30px;
            }

            QComboBox#formCombo::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #718096;
                margin-right: 10px;
            }

            QTextEdit#formTextArea {
                background: white;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: #4a5568;
            }

            QTextEdit#formTextArea:focus {
                border-color: #667eea;
                background: #f8fafc;
            }

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

            QLabel {
                color: #4a5568;
                font-weight: 600;
                font-size: 14px;
            }
        """)

    def load_contact_data(self):
        """Load existing contact data into the form."""
        if not self.contact:
            return

        self.name_edit.setText(self.contact.name or "")
        self.email_edit.setText(self.contact.email or "")
        self.codementor_edit.setText(self.contact.codementor_username or "")
        self.platform_combo.setCurrentText(self.contact.platform_preference or "email")
        self.notes_edit.setPlainText(self.contact.notes or "")

    def save_contact(self):
        """Save the contact to the database."""
        # Validate required fields
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Name is required.")
            self.name_edit.setFocus()
            return

        try:
            db = next(get_db())

            if self.contact:
                # Update existing contact
                self.contact.name = self.name_edit.text().strip()
                self.contact.email = self.email_edit.text().strip() or None
                self.contact.codementor_username = self.codementor_edit.text().strip() or None
                self.contact.platform_preference = self.platform_combo.currentText()
                self.contact.notes = self.notes_edit.toPlainText().strip() or None
                self.contact.updated_at = datetime.now(timezone.utc)
            else:
                # Create new contact
                contact = Contact(
                    name=self.name_edit.text().strip(),
                    email=self.email_edit.text().strip() or None,
                    codementor_username=self.codementor_edit.text().strip() or None,
                    platform_preference=self.platform_combo.currentText(),
                    notes=self.notes_edit.toPlainText().strip() or None
                )
                db.add(contact)

            db.commit()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save contact: {str(e)}")
            db.rollback()

    def get_contact(self):
        """Get the contact object (for new contacts)."""
        return self.contact
