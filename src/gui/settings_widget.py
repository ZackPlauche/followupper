"""Settings and credentials management widget."""

from ..models.platform_credentials import PlatformCredentials
from ..models.database import get_db
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox,
    QGroupBox, QTextEdit, QCheckBox, QTabWidget
)
from PySide6.QtCore import Qt, Signal
from cryptography.fernet import Fernet
import base64
import json
import os


class SettingsWidget(QWidget):
    """Widget for managing application settings and credentials."""

    settings_updated = Signal()  # Signal emitted when settings are updated

    def __init__(self, parent=None):
        super().__init__(parent)
        self.encryption_key = self.get_or_create_encryption_key()
        self.setup_ui()
        self.load_settings()

    def get_or_create_encryption_key(self):
        """Get or create encryption key for credentials."""
        key_file = "encryption.key"
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Create tab widget for different settings
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Credentials tab
        self.create_credentials_tab()

        # General settings tab
        self.create_general_tab()

        # About tab
        self.create_about_tab()

    def create_credentials_tab(self):
        """Create credentials management tab."""
        credentials_widget = QWidget()
        layout = QVBoxLayout(credentials_widget)

        # Gmail credentials
        gmail_group = QGroupBox("Gmail Credentials")
        gmail_layout = QFormLayout(gmail_group)

        self.gmail_client_id = QLineEdit()
        self.gmail_client_id.setPlaceholderText("Enter Gmail Client ID")
        gmail_layout.addRow("Client ID:", self.gmail_client_id)

        self.gmail_client_secret = QLineEdit()
        self.gmail_client_secret.setEchoMode(QLineEdit.Password)
        self.gmail_client_secret.setPlaceholderText("Enter Gmail Client Secret")
        gmail_layout.addRow("Client Secret:", self.gmail_client_secret)

        self.gmail_refresh_token = QLineEdit()
        self.gmail_refresh_token.setEchoMode(QLineEdit.Password)
        self.gmail_refresh_token.setPlaceholderText("Enter Gmail Refresh Token")
        gmail_layout.addRow("Refresh Token:", self.gmail_refresh_token)

        gmail_save_btn = QPushButton("Save Gmail Credentials")
        gmail_save_btn.clicked.connect(self.save_gmail_credentials)
        gmail_layout.addRow("", gmail_save_btn)

        layout.addWidget(gmail_group)

        # Codementor credentials
        codementor_group = QGroupBox("Codementor Credentials")
        codementor_layout = QFormLayout(codementor_group)

        self.codementor_api_key = QLineEdit()
        self.codementor_api_key.setEchoMode(QLineEdit.Password)
        self.codementor_api_key.setPlaceholderText("Enter Codementor API Key")
        codementor_layout.addRow("API Key:", self.codementor_api_key)

        codementor_save_btn = QPushButton("Save Codementor Credentials")
        codementor_save_btn.clicked.connect(self.save_codementor_credentials)
        codementor_layout.addRow("", codementor_save_btn)

        layout.addWidget(codementor_group)

        # Test credentials
        test_layout = QHBoxLayout()
        test_gmail_btn = QPushButton("Test Gmail Connection")
        test_gmail_btn.clicked.connect(self.test_gmail_connection)
        test_layout.addWidget(test_gmail_btn)

        test_codementor_btn = QPushButton("Test Codementor Connection")
        test_codementor_btn.clicked.connect(self.test_codementor_connection)
        test_layout.addWidget(test_codementor_btn)

        layout.addLayout(test_layout)
        layout.addStretch()

        self.tab_widget.addTab(credentials_widget, "Credentials")

    def create_general_tab(self):
        """Create general settings tab."""
        general_widget = QWidget()
        layout = QVBoxLayout(general_widget)

        # Application settings
        app_group = QGroupBox("Application Settings")
        app_layout = QFormLayout(app_group)

        self.auto_start_checkbox = QCheckBox("Start with Windows")
        app_layout.addRow("", self.auto_start_checkbox)

        self.minimize_to_tray_checkbox = QCheckBox("Minimize to system tray")
        app_layout.addRow("", self.minimize_to_tray_checkbox)

        self.auto_schedule_checkbox = QCheckBox("Automatically schedule follow-ups")
        app_layout.addRow("", self.auto_schedule_checkbox)

        layout.addWidget(app_group)

        # Notification settings
        notif_group = QGroupBox("Notification Settings")
        notif_layout = QFormLayout(notif_group)

        self.email_notifications_checkbox = QCheckBox("Email notifications for failed follow-ups")
        notif_layout.addRow("", self.email_notifications_checkbox)

        self.desktop_notifications_checkbox = QCheckBox("Desktop notifications")
        notif_layout.addRow("", self.desktop_notifications_checkbox)

        layout.addWidget(notif_group)

        # Save settings button
        save_settings_btn = QPushButton("Save Settings")
        save_settings_btn.clicked.connect(self.save_general_settings)
        layout.addWidget(save_settings_btn)

        layout.addStretch()

        self.tab_widget.addTab(general_widget, "General")

    def create_about_tab(self):
        """Create about tab."""
        about_widget = QWidget()
        layout = QVBoxLayout(about_widget)

        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setHtml("""
        <h2>Followupper v0.1.0</h2>
        <p>Automated follow-up application for managing client communications across multiple platforms.</p>

        <h3>Features:</h3>
        <ul>
        <li>Contact management with custom follow-up frequencies</li>
        <li>Message templates for different platforms</li>
        <li>Automated scheduling with APScheduler</li>
        <li>Gmail and Codementor integration</li>
        <li>Background operation with system tray</li>
        <li>Failed message retry mechanisms</li>
        </ul>

        <h3>Built with:</h3>
        <ul>
        <li>PySide6 - GUI framework</li>
        <li>SQLAlchemy - Database ORM</li>
        <li>Alembic - Database migrations</li>
        <li>APScheduler - Job scheduling</li>
        <li>Cryptography - Credential encryption</li>
        </ul>

        <h3>Links:</h3>
        <ul>
        <li>Gmail Client: <a href="https://github.com/zackplauche/python-gmail">https://github.com/zackplauche/python-gmail</a></li>
        <li>Codementor API: <a href="https://github.com/zackplauche/codementorapi">https://github.com/zackplauche/codementorapi</a></li>
        </ul>
        """)

        layout.addWidget(about_text)

        self.tab_widget.addTab(about_widget, "About")

    def load_settings(self):
        """Load settings from database."""
        try:
            db = next(get_db())

            # Load Gmail credentials
            gmail_creds = db.query(PlatformCredentials).filter(
                PlatformCredentials.platform == 'gmail'
            ).first()

            if gmail_creds:
                decrypted = self.decrypt_credentials(gmail_creds.encrypted_credentials)
                if decrypted:
                    self.gmail_client_id.setText(decrypted.get('client_id', ''))
                    self.gmail_client_secret.setText(decrypted.get('client_secret', ''))
                    self.gmail_refresh_token.setText(decrypted.get('refresh_token', ''))

            # Load Codementor credentials
            codementor_creds = db.query(PlatformCredentials).filter(
                PlatformCredentials.platform == 'codementor'
            ).first()

            if codementor_creds:
                decrypted = self.decrypt_credentials(codementor_creds.encrypted_credentials)
                if decrypted:
                    self.codementor_api_key.setText(decrypted.get('api_key', ''))

        except Exception as e:
            QMessageBox.warning(self, "Settings Error", f"Failed to load settings: {str(e)}")

    def save_gmail_credentials(self):
        """Save Gmail credentials."""
        try:
            credentials = {
                'client_id': self.gmail_client_id.text().strip(),
                'client_secret': self.gmail_client_secret.text().strip(),
                'refresh_token': self.gmail_refresh_token.text().strip()
            }

            if not all(credentials.values()):
                QMessageBox.warning(self, "Validation Error", "Please fill in all Gmail credential fields.")
                return

            self.save_platform_credentials('gmail', credentials)
            QMessageBox.information(self, "Success", "Gmail credentials saved successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save Gmail credentials: {str(e)}")

    def save_codementor_credentials(self):
        """Save Codementor credentials."""
        try:
            api_key = self.codementor_api_key.text().strip()

            if not api_key:
                QMessageBox.warning(self, "Validation Error", "Please enter the Codementor API key.")
                return

            credentials = {'api_key': api_key}
            self.save_platform_credentials('codementor', credentials)
            QMessageBox.information(self, "Success", "Codementor credentials saved successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save Codementor credentials: {str(e)}")

    def save_platform_credentials(self, platform, credentials):
        """Save encrypted platform credentials."""
        try:
            db = next(get_db())

            # Encrypt credentials
            encrypted = self.encrypt_credentials(credentials)

            # Save or update credentials
            existing = db.query(PlatformCredentials).filter(
                PlatformCredentials.platform == platform
            ).first()

            if existing:
                existing.encrypted_credentials = encrypted
            else:
                creds = PlatformCredentials(
                    platform=platform,
                    encrypted_credentials=encrypted
                )
                db.add(creds)

            db.commit()
            self.settings_updated.emit()

        except Exception as e:
            db.rollback()
            raise e

    def encrypt_credentials(self, credentials):
        """Encrypt credentials using Fernet."""
        f = Fernet(self.encryption_key)
        json_str = json.dumps(credentials)
        return f.encrypt(json_str.encode()).decode()

    def decrypt_credentials(self, encrypted_credentials):
        """Decrypt credentials using Fernet."""
        try:
            f = Fernet(self.encryption_key)
            decrypted = f.decrypt(encrypted_credentials.encode())
            return json.loads(decrypted.decode())
        except Exception:
            return None

    def save_general_settings(self):
        """Save general application settings."""
        # TODO: Implement general settings storage
        QMessageBox.information(self, "Settings Saved", "General settings saved successfully.")

    def test_gmail_connection(self):
        """Test Gmail connection."""
        # TODO: Implement Gmail connection test
        QMessageBox.information(self, "Gmail Test", "Gmail connection test will be implemented here.")

    def test_codementor_connection(self):
        """Test Codementor connection."""
        # TODO: Implement Codementor connection test
        QMessageBox.information(self, "Codementor Test", "Codementor connection test will be implemented here.")
