"""Main application window with modern UI."""

from .settings_widget import SettingsWidget
from .schedule_widget import ScheduleWidget
from .templates_widget import TemplatesWidget
from .contacts_widget import ContactsWidget
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..models.scheduled_followup import ScheduledFollowup
from ..models.contact import Contact
from ..models.database import get_db
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QStatusBar,
    QMenuBar, QMenu, QSystemTrayIcon, QMessageBox,
    QFrame, QSplitter, QScrollArea, QStackedWidget
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, Signal
from PySide6.QtGui import QAction, QIcon, QPalette, QColor, QFont, QLinearGradient, QPainter


class ModernButton(QPushButton):
    """Modern styled button with hover effects."""

    def __init__(self, text, icon=None, parent=None):
        super().__init__(text, parent)
        self.setObjectName("modernButton")
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)

        # Add icon if provided
        if icon:
            self.setIcon(icon)

    def enterEvent(self, event):
        """Hover enter effect."""
        self.setStyleSheet("""
            QPushButton#modernButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton#modernButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a6fd8, stop:1 #6a4190);
            }
            QPushButton#modernButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4c63d2, stop:1 #5e3a7e);
            }
        """)


class SidebarButton(QPushButton):
    """Sidebar navigation button."""

    clicked_signal = Signal(str)

    def __init__(self, text, icon_text, section, parent=None):
        super().__init__(text, parent)
        self.section = section
        self.icon_text = icon_text
        self.setObjectName("sidebarButton")
        self.setMinimumHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self.clicked.connect(lambda: self.clicked_signal.emit(self.section))

    def paintEvent(self, event):
        """Custom paint event for icon and text."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background
        if self.isChecked():
            painter.fillRect(self.rect(), QColor(102, 126, 234, 100))
        elif self.underMouse():
            painter.fillRect(self.rect(), QColor(102, 126, 234, 50))

        # Icon (using text as icon for simplicity)
        painter.setFont(QFont("Arial", 16, QFont.Bold))
        painter.setPen(QColor(102, 126, 234) if self.isChecked() else QColor(100, 100, 100))
        painter.drawText(20, 20, self.icon_text)

        # Text
        painter.setFont(QFont("Arial", 12, QFont.Medium))
        painter.setPen(QColor(50, 50, 50) if self.isChecked() else QColor(100, 100, 100))
        painter.drawText(60, 25, self.text())


class MainWindow(QMainWindow):
    """Modern main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Followupper - Automated Follow-up Manager")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)

        # Apply modern styling
        self.apply_modern_styling()

        # Create central widget with modern layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setObjectName("centralWidget")

        # Main layout with sidebar and content area
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create sidebar
        self.create_sidebar(main_layout)

        # Create content area
        self.create_content_area(main_layout)

        # Create status bar
        self.create_modern_status_bar()

        # Create menu bar
        self.create_menu_bar()

        # Create system tray (disabled for now)
        # self.create_system_tray()

        # Start status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(30000)  # Update every 30 seconds

    def apply_modern_styling(self):
        """Apply modern styling to the application."""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8fafc, stop:1 #e2e8f0);
            }

            QWidget#centralWidget {
                background: transparent;
            }

            QFrame#sidebar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border-right: 1px solid #e2e8f0;
            }

            QFrame#contentArea {
                background: transparent;
                border-radius: 12px;
                margin: 8px;
            }

            QLabel#titleLabel {
                font-size: 24px;
                font-weight: 700;
                color: #1a202c;
                margin: 20px 0px 10px 0px;
            }

            QLabel#subtitleLabel {
                font-size: 14px;
                color: #718096;
                margin-bottom: 20px;
            }

            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border-top: 1px solid #e2e8f0;
                color: #4a5568;
                font-size: 12px;
            }

            QMenuBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border-bottom: 1px solid #e2e8f0;
                color: #4a5568;
                font-size: 13px;
            }

            QMenuBar::item {
                background: transparent;
                padding: 8px 12px;
                border-radius: 4px;
            }

            QMenuBar::item:selected {
                background: #667eea;
                color: white;
            }

            QMenu {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 4px;
            }

            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
            }

            QMenu::item:selected {
                background: #667eea;
                color: white;
            }
        """)

    def create_sidebar(self, parent_layout):
        """Create modern sidebar navigation."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        sidebar.setFrameStyle(QFrame.NoFrame)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # App title
        title = QLabel("📧 Followupper")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        subtitle = QLabel("Automated Follow-up Manager")
        subtitle.setObjectName("subtitleLabel")
        layout.addWidget(subtitle)

        # Navigation buttons
        self.nav_buttons = {}
        sections = [
            ("👥", "Contacts", "contacts"),
            ("📝", "Templates", "templates"),
            ("📅", "Schedule", "schedule"),
            ("⚙️", "Settings", "settings")
        ]

        for icon, text, section in sections:
            btn = SidebarButton(text, icon, section)
            btn.clicked_signal.connect(self.navigate_to_section)
            self.nav_buttons[section] = btn
            layout.addWidget(btn)

        # Set first button as active
        self.nav_buttons["contacts"].setChecked(True)

        # Add stretch to push buttons to top
        layout.addStretch()

        # Add to parent layout
        parent_layout.addWidget(sidebar)

    def create_content_area(self, parent_layout):
        """Create main content area with stacked widgets."""
        content_frame = QFrame()
        content_frame.setObjectName("contentArea")
        content_frame.setFrameStyle(QFrame.NoFrame)

        layout = QVBoxLayout(content_frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)

        # Create stacked widget for different sections
        self.stacked_widget = QStackedWidget()

        # Create and add widgets
        self.contacts_widget = ContactsWidget()
        self.templates_widget = TemplatesWidget()
        self.schedule_widget = ScheduleWidget()
        self.settings_widget = SettingsWidget()

        self.stacked_widget.addWidget(self.contacts_widget)
        self.stacked_widget.addWidget(self.templates_widget)
        self.stacked_widget.addWidget(self.schedule_widget)
        self.stacked_widget.addWidget(self.settings_widget)

        layout.addWidget(self.stacked_widget)

        # Add to parent layout
        parent_layout.addWidget(content_frame)

    def navigate_to_section(self, section):
        """Navigate to the specified section."""
        # Update button states
        for btn in self.nav_buttons.values():
            btn.setChecked(False)
        self.nav_buttons[section].setChecked(True)

        # Switch to the appropriate widget
        section_map = {
            "contacts": 0,
            "templates": 1,
            "schedule": 2,
            "settings": 3
        }

        self.stacked_widget.setCurrentIndex(section_map[section])

    def create_modern_status_bar(self):
        """Create modern status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("🚀 Ready - All systems operational")
        self.update_status()

    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('&File')

        # New Contact action
        new_contact_action = QAction('&New Contact', self)
        new_contact_action.setShortcut('Ctrl+N')
        new_contact_action.triggered.connect(self.contacts_widget.add_contact)
        file_menu.addAction(new_contact_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu('&View')

        # Refresh action
        refresh_action = QAction('&Refresh', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_all)
        view_menu.addAction(refresh_action)

        # Help menu
        help_menu = menubar.addMenu('&Help')

        # About action
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_system_tray(self):
        """Create system tray icon."""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            # Use a simple icon or create a custom one
            try:
                self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_MessageBoxInformation))
            except BaseException:
                # If no icon available, just create without icon
                pass

            # Create tray menu
            tray_menu = QMenu()

            show_action = QAction("Show", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)

            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(self.close)
            tray_menu.addAction(quit_action)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()

    def refresh_all(self):
        """Refresh all widgets."""
        self.contacts_widget.refresh()
        self.templates_widget.refresh()
        self.schedule_widget.refresh()
        self.status_bar.showMessage("🔄 Refreshed - All data updated")

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About Followupper",
                          "Followupper v1.0\n\n"
                          "A modern, automated follow-up management system.\n"
                          "Built with PySide6 and Python.")

    def update_status(self):
        """Update status bar with current information."""
        try:
            db = next(get_db())

            # Get counts
            total_contacts = db.query(Contact).count()
            active_contacts = db.query(Contact).filter(Contact.is_active == True).count()
            pending_followups = db.query(ScheduledFollowup).filter(
                ScheduledFollowup.scheduled_time > func.now()
            ).count()

            status_text = f"👥 {active_contacts}/{total_contacts} contacts | 📅 {pending_followups} pending follow-ups | 🚀 Ready"
            self.status_bar.showMessage(status_text)

        except Exception as e:
            self.status_bar.showMessage(f"⚠️ Error: {str(e)}")

    def closeEvent(self, event):
        """Handle application close event."""
        reply = QMessageBox.question(self, 'Exit Followupper',
                                     'Are you sure you want to exit?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
