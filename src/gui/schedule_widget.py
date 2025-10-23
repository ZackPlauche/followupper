"""Schedule management widget."""

from ..models.message_template import MessageTemplate
from ..models.contact import Contact
from ..models.scheduled_followup import ScheduledFollowup
from ..models.database import get_db
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QHeaderView, QMessageBox,
    QMenu, QAbstractItemView, QComboBox, QLabel, QDateEdit
)
from PySide6.QtCore import Qt, Signal, QDate, QDateTime
from PySide6.QtGui import QAction
from datetime import datetime, timedelta, timezone


class ScheduleWidget(QWidget):
    """Widget for managing scheduled follow-ups."""

    schedule_updated = Signal()  # Signal emitted when schedule is updated

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_schedule()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Header with buttons and filters
        header_layout = QHBoxLayout()

        schedule_btn = QPushButton("Schedule New Follow-up")
        schedule_btn.clicked.connect(self.schedule_followup)
        header_layout.addWidget(schedule_btn)

        retry_btn = QPushButton("Retry Failed")
        retry_btn.clicked.connect(self.retry_failed)
        header_layout.addWidget(retry_btn)

        header_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Pending", "Sent", "Failed", "Overdue"])
        self.status_filter.currentTextChanged.connect(self.load_schedule)
        header_layout.addWidget(self.status_filter)

        header_layout.addWidget(QLabel("From:"))
        self.date_filter = QDateEdit()
        self.date_filter.setDate(QDate.currentDate().addDays(-30))
        self.date_filter.dateChanged.connect(self.load_schedule)
        header_layout.addWidget(self.date_filter)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_schedule)
        header_layout.addWidget(refresh_btn)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Schedule table
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(7)
        self.schedule_table.setHorizontalHeaderLabels([
            "Contact", "Template", "Platform", "Scheduled", "Status", "Sent", "Error"
        ])

        # Configure table
        self.schedule_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.schedule_table.setAlternatingRowColors(True)
        self.schedule_table.setSortingEnabled(True)

        # Set column widths
        header = self.schedule_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Contact
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Template
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Platform
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Scheduled
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Sent
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Error

        layout.addWidget(self.schedule_table)

        # Context menu
        self.schedule_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.schedule_table.customContextMenuRequested.connect(self.show_context_menu)

    def load_schedule(self):
        """Load scheduled follow-ups from database and populate table."""
        try:
            db = next(get_db())

            # Apply filters
            query = db.query(ScheduledFollowup).join(Contact).join(MessageTemplate)

            # Status filter
            status_filter = self.status_filter.currentText()
            if status_filter == "Pending":
                query = query.filter(ScheduledFollowup.status == 'pending')
            elif status_filter == "Sent":
                query = query.filter(ScheduledFollowup.status == 'sent')
            elif status_filter == "Failed":
                query = query.filter(ScheduledFollowup.status == 'failed')
            elif status_filter == "Overdue":
                query = query.filter(
                    ScheduledFollowup.status == 'pending',
                    ScheduledFollowup.scheduled_date < datetime.now(timezone.utc)
                )

            # Date filter
            from_date = self.date_filter.date().toPython()
            query = query.filter(ScheduledFollowup.scheduled_date >= from_date)

            followups = query.order_by(ScheduledFollowup.scheduled_date.desc()).all()

            self.schedule_table.setRowCount(len(followups))

            for row, followup in enumerate(followups):
                # Contact name
                contact_name = followup.contact.name if followup.contact else "Unknown"
                self.schedule_table.setItem(row, 0, QTableWidgetItem(contact_name))

                # Template name
                template_name = followup.template.name if followup.template else "Unknown"
                self.schedule_table.setItem(row, 1, QTableWidgetItem(template_name))

                # Platform
                self.schedule_table.setItem(row, 2, QTableWidgetItem(followup.platform))

                # Scheduled date
                scheduled = followup.scheduled_date.strftime("%Y-%m-%d %H:%M") if followup.scheduled_date else "Unknown"
                self.schedule_table.setItem(row, 3, QTableWidgetItem(scheduled))

                # Status with color coding
                status_item = QTableWidgetItem(followup.status or "Unknown")
                if followup.status == 'sent':
                    status_item.setBackground(Qt.green)
                elif followup.status == 'failed':
                    status_item.setBackground(Qt.red)
                elif followup.status == 'pending':
                    if followup.scheduled_date and followup.scheduled_date < datetime.now(timezone.utc):
                        status_item.setBackground(Qt.yellow)  # Overdue
                    else:
                        status_item.setBackground(Qt.blue)
                self.schedule_table.setItem(row, 4, status_item)

                # Sent date
                sent_date = followup.sent_date.strftime("%Y-%m-%d %H:%M") if followup.sent_date else "Not sent"
                self.schedule_table.setItem(row, 5, QTableWidgetItem(sent_date))

                # Error message
                error = followup.error_message or ""
                self.schedule_table.setItem(row, 6, QTableWidgetItem(error))

                # Store followup ID in the row data
                self.schedule_table.item(row, 0).setData(Qt.UserRole, followup.id)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load schedule: {str(e)}")

    def get_selected_followup_id(self):
        """Get the ID of the currently selected follow-up."""
        current_row = self.schedule_table.currentRow()
        if current_row >= 0:
            item = self.schedule_table.item(current_row, 0)
            if item:
                return item.data(Qt.UserRole)
        return None

    def get_selected_followup(self):
        """Get the currently selected follow-up from database."""
        followup_id = self.get_selected_followup_id()
        if not followup_id:
            return None

        try:
            db = next(get_db())
            return db.query(ScheduledFollowup).filter(ScheduledFollowup.id == followup_id).first()
        except Exception:
            return None

    def schedule_followup(self):
        """Schedule a new follow-up."""
        # TODO: Implement schedule follow-up dialog
        QMessageBox.information(self, "Schedule Follow-up", "Schedule follow-up dialog will be implemented here")

    def retry_failed(self):
        """Retry failed follow-ups."""
        try:
            db = next(get_db())
            failed_followups = db.query(ScheduledFollowup).filter(
                ScheduledFollowup.status == 'failed'
            ).all()

            if not failed_followups:
                QMessageBox.information(self, "No Failed Follow-ups", "No failed follow-ups to retry.")
                return

            reply = QMessageBox.question(
                self,
                "Retry Failed Follow-ups",
                f"Retry {len(failed_followups)} failed follow-ups?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Reset failed follow-ups to pending
                for followup in failed_followups:
                    followup.status = 'pending'
                    followup.error_message = None
                    followup.retry_count += 1

                db.commit()
                self.load_schedule()
                self.schedule_updated.emit()
                QMessageBox.information(self, "Success", f"Retried {len(failed_followups)} failed follow-ups.")

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to retry failed follow-ups: {str(e)}")

    def show_context_menu(self, position):
        """Show context menu for the table."""
        if self.schedule_table.itemAt(position) is None:
            return

        followup = self.get_selected_followup()
        if not followup:
            return

        menu = QMenu(self)

        if followup.status == 'failed':
            retry_action = QAction("Retry Follow-up", self)
            retry_action.triggered.connect(self.retry_selected)
            menu.addAction(retry_action)

        if followup.status == 'pending':
            cancel_action = QAction("Cancel Follow-up", self)
            cancel_action.triggered.connect(self.cancel_selected)
            menu.addAction(cancel_action)

        menu.exec(self.schedule_table.mapToGlobal(position))

    def retry_selected(self):
        """Retry the selected follow-up."""
        followup = self.get_selected_followup()
        if not followup:
            return

        try:
            db = next(get_db())
            followup.status = 'pending'
            followup.error_message = None
            followup.retry_count += 1
            db.commit()

            self.load_schedule()
            self.schedule_updated.emit()
            QMessageBox.information(self, "Success", "Follow-up retry scheduled.")

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to retry follow-up: {str(e)}")

    def cancel_selected(self):
        """Cancel the selected follow-up."""
        followup = self.get_selected_followup()
        if not followup:
            return

        reply = QMessageBox.question(
            self,
            "Cancel Follow-up",
            f"Cancel this follow-up?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                db = next(get_db())
                followup.status = 'cancelled'
                db.commit()

                self.load_schedule()
                self.schedule_updated.emit()
                QMessageBox.information(self, "Success", "Follow-up cancelled.")

            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to cancel follow-up: {str(e)}")
