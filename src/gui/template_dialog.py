"""Message template management dialog."""

from ..models.message_template import MessageTemplate
from ..models.database import get_db
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QPushButton, QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt
from datetime import datetime, timezone


class TemplateDialog(QDialog):
    """Dialog for adding/editing message templates."""

    def __init__(self, template=None, parent=None):
        super().__init__(parent)
        self.template = template
        self.setWindowTitle("Add Template" if not template else "Edit Template")
        self.setModal(True)
        self.setFixedSize(600, 500)

        self.setup_ui()
        if template:
            self.load_template_data()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()

        # Template name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter template name")
        form_layout.addRow("Name *:", self.name_edit)

        # Platform selection
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["email", "codementor"])
        form_layout.addRow("Platform *:", self.platform_combo)

        # Subject (for email templates)
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("Enter email subject")
        form_layout.addRow("Subject:", self.subject_edit)

        # Message body
        self.body_edit = QTextEdit()
        self.body_edit.setPlaceholderText("Enter your message template here...\n\nYou can use variables like:\n- {name} - Contact name\n- {email} - Contact email")
        self.body_edit.setMinimumHeight(200)
        form_layout.addRow("Message Body *:", self.body_edit)

        # Default template checkbox
        self.default_checkbox = QCheckBox("Set as default template for this platform")
        form_layout.addRow("", self.default_checkbox)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.save_template)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_template_data(self):
        """Load existing template data into the form."""
        if not self.template:
            return

        self.name_edit.setText(self.template.name or "")
        self.platform_combo.setCurrentText(self.template.platform or "email")
        self.subject_edit.setText(self.template.subject or "")
        self.body_edit.setPlainText(self.template.body or "")
        self.default_checkbox.setChecked(self.template.is_default or False)

    def save_template(self):
        """Save the template to the database."""
        # Validate required fields
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Template name is required.")
            return

        if not self.body_edit.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", "Message body is required.")
            return

        try:
            db = next(get_db())

            # If setting as default, unset other defaults for this platform
            if self.default_checkbox.isChecked():
                db.query(MessageTemplate).filter(
                    MessageTemplate.platform == self.platform_combo.currentText(),
                    MessageTemplate.is_default == True
                ).update({"is_default": False})

            if self.template:
                # Update existing template
                self.template.name = self.name_edit.text().strip()
                self.template.platform = self.platform_combo.currentText()
                self.template.subject = self.subject_edit.text().strip() or None
                self.template.body = self.body_edit.toPlainText().strip()
                self.template.is_default = self.default_checkbox.isChecked()
                self.template.updated_at = datetime.now(timezone.utc)
            else:
                # Create new template
                template = MessageTemplate(
                    name=self.name_edit.text().strip(),
                    platform=self.platform_combo.currentText(),
                    subject=self.subject_edit.text().strip() or None,
                    body=self.body_edit.toPlainText().strip(),
                    is_default=self.default_checkbox.isChecked()
                )
                db.add(template)

            db.commit()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save template: {str(e)}")
            db.rollback()

    def get_template(self):
        """Get the template object (for new templates)."""
        return self.template
