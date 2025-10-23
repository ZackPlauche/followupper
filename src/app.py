"""Simple CustomTkinter application that actually works."""

import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timezone
import threading
import sys

from .models.database import engine, Base
from .models.contact import Contact
from .models.message_template import MessageTemplate
from .models.scheduled_followup import ScheduledFollowup
from .models.platform_credentials import PlatformCredentials
from .models.followup_sequence import FollowupSequence
from .models.followup_sequence_step import FollowupSequenceStep
from .models.contact_sequence_assignment import ContactSequenceAssignment
from sqlalchemy.orm import Session


def with_surrogates(text):
    """Convert emoji and other non-BMP characters to surrogate pairs for tkinter compatibility."""
    return text.encode('utf-16le').decode('utf-16le')


class TemplateDialog(ctk.CTkToplevel):
    """Template dialog for adding/editing message templates."""

    def __init__(self, parent, template=None):
        super().__init__(parent)
        self.template = template
        self.result = None

        self.title("Add Template" if not template else "Edit Template")
        self.geometry("600x700")
        self.resizable(False, False)

        # Center the window
        self.transient(parent)
        self.grab_set()

        self.setup_ui()

        if template:
            self.load_template_data()

    def setup_ui(self):
        """Set up the UI."""
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(main_frame, text="Message Template", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=(0, 20))

        # Template name
        ctk.CTkLabel(main_frame, text="Template Name *").pack(anchor="w", pady=(0, 5))
        self.name_var = tk.StringVar()
        self.name_entry = ctk.CTkEntry(main_frame, textvariable=self.name_var, width=500)
        self.name_entry.pack(fill="x", pady=(0, 15))

        # Subject
        ctk.CTkLabel(main_frame, text="Subject").pack(anchor="w", pady=(0, 5))
        self.subject_text = ctk.CTkTextbox(main_frame, width=500, height=80, font=ctk.CTkFont(family="Segoe UI Emoji", size=12))
        self.subject_text.pack(fill="x", pady=(0, 15))

        # Body
        ctk.CTkLabel(main_frame, text="Message Body *").pack(anchor="w", pady=(0, 5))
        self.body_text = ctk.CTkTextbox(main_frame, width=500, height=200, font=ctk.CTkFont(family="Segoe UI Emoji", size=12))
        self.body_text.pack(fill="x", pady=(0, 15))

        # Template variables help
        help_frame = ctk.CTkFrame(main_frame)
        help_frame.pack(fill="x", pady=(0, 15))

        # Add emoji processing info
        emoji_info = ctk.CTkLabel(help_frame,
                                  text="💡 Tip: You can use emoji codes like :smile: or :heart: which will be converted to emojis!",
                                  font=ctk.CTkFont(size=11))
        emoji_info.pack(anchor="w", pady=(5, 0))

        # Bind emoji processing to text changes
        self.subject_text.bind('<KeyRelease>', self.process_emojis_realtime)
        self.body_text.bind('<KeyRelease>', self.process_emojis_realtime)

        ctk.CTkLabel(help_frame, text="Available Variables:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)

        variables_text = """{user.first_name} - First name
{user.last_name} - Last name
{user.email} - Email address
{user.codementor_username} - Codementor username
{user.platform_preference} - Platform preference
{user.notes} - Notes
{contact.first_name} - First name (alternative)
{contact.email} - Email address (alternative)"""

        variables_label = ctk.CTkLabel(help_frame, text=variables_text, font=ctk.CTkFont(size=12))
        variables_label.pack(anchor="w", padx=10, pady=5)

        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(button_frame, text="Cancel", command=self.cancel, width=100).pack(side="right", padx=(10, 0))
        ctk.CTkButton(button_frame, text="Preview", command=self.preview_template, width=100).pack(side="right", padx=(10, 0))
        ctk.CTkButton(button_frame, text="Save", command=self.save, width=100).pack(side="right")

    def load_template_data(self):
        """Load existing template data."""
        if not self.template:
            return

        self.name_var.set(self.template.name or "")
        self.subject_text.insert("1.0", self.template.subject or "")
        self.body_text.insert("1.0", self.template.body or "")

    def preview_template(self):
        """Preview template with sample data."""
        # Get first contact for preview
        try:
            db = Session(engine)
            contact = db.query(Contact).first()
            db.close()

            if not contact:
                messagebox.showinfo("Preview", "No contacts available for preview. Add a contact first.")
                return

            # Create a temporary template for preview
            temp_template = MessageTemplate(
                name=self.name_var.get(),
                subject=self.subject_text.get("1.0", "end-1c"),
                body=self.body_text.get("1.0", "end-1c")
            )

            # Render the template
            rendered = temp_template.render_template(contact)

            # Show preview dialog
            preview_dialog = ctk.CTkToplevel(self)
            preview_dialog.title("Template Preview")
            preview_dialog.geometry("500x400")

            preview_frame = ctk.CTkFrame(preview_dialog)
            preview_frame.pack(fill="both", expand=True, padx=20, pady=20)

            ctk.CTkLabel(preview_frame, text="Preview with Contact Data:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 10))

            ctk.CTkLabel(preview_frame, text=f"Contact: {contact.name}").pack(anchor="w", pady=(0, 5))

            ctk.CTkLabel(preview_frame, text="Subject:").pack(anchor="w", pady=(10, 5))
            subject_preview = ctk.CTkTextbox(preview_frame, height=60, font=ctk.CTkFont(family="Segoe UI Emoji", size=12))
            subject_preview.pack(fill="x", pady=(0, 10))
            subject_preview.insert("1.0", with_surrogates(rendered['subject']))
            subject_preview.configure(state="disabled")

            ctk.CTkLabel(preview_frame, text="Body:").pack(anchor="w", pady=(0, 5))
            body_preview = ctk.CTkTextbox(preview_frame, height=150, font=ctk.CTkFont(family="Segoe UI Emoji", size=12))
            body_preview.pack(fill="both", expand=True)
            body_preview.insert("1.0", with_surrogates(rendered['body']))
            body_preview.configure(state="disabled")

            ctk.CTkButton(preview_frame, text="Close", command=preview_dialog.destroy).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Preview Error", f"Failed to preview template: {str(e)}")

    def process_emojis_realtime(self, event):
        """Process emojis in real-time as user types."""
        try:
            import emoji
            widget = event.widget

            # Get current text
            current_text = widget.get("1.0", "end-1c")

            # Process emojis
            processed_text = emoji.emojize(current_text, use_aliases=True)

            # If text changed, update the widget
            if processed_text != current_text:
                # Get cursor position
                cursor_pos = widget.index(tk.INSERT)

                # Update text
                widget.delete("1.0", "end-1c")
                widget.insert("1.0", with_surrogates(processed_text))

                # Restore cursor position
                try:
                    widget.mark_set(tk.INSERT, cursor_pos)
                except BaseException:
                    pass

        except Exception as e:
            # Don't show error for emoji processing
            pass

    def save(self):
        """Save the template."""
        if not self.name_var.get().strip():
            messagebox.showerror("Error", "Template name is required.")
            return

        if not self.body_text.get("1.0", "end-1c").strip():
            messagebox.showerror("Error", "Message body is required.")
            return

        try:
            db = Session(engine)

            if self.template:
                # Update existing template
                self.template.name = self.name_var.get().strip()
                self.template.subject = self.subject_text.get("1.0", "end-1c").strip()
                self.template.body = self.body_text.get("1.0", "end-1c").strip()
                self.template.updated_at = datetime.now(timezone.utc)
            else:
                # Create new template
                template = MessageTemplate(
                    name=self.name_var.get().strip(),
                    subject=self.subject_text.get("1.0", "end-1c").strip(),
                    body=self.body_text.get("1.0", "end-1c").strip()
                )
                db.add(template)

            db.commit()
            db.close()

            self.result = True
            self.destroy()

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save template: {str(e)}")

    def cancel(self):
        """Cancel the dialog."""
        self.result = False
        self.destroy()


class ContactDialog(ctk.CTkToplevel):
    """Simple contact dialog."""

    def __init__(self, parent, contact=None):
        super().__init__(parent)
        self.contact = contact
        self.result = None

        self.title("Add Contact" if not contact else "Edit Contact")
        self.geometry("400x500")
        self.resizable(False, False)

        # Center the window
        self.transient(parent)
        self.grab_set()

        self.setup_ui()

        if contact:
            self.load_contact_data()

    def setup_ui(self):
        """Set up the UI."""
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(main_frame, text="Contact Details", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=(0, 20))

        # Form fields
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.codementor_var = tk.StringVar()
        self.platform_var = tk.StringVar(value="email")
        self.notes_var = tk.StringVar()

        # Name
        ctk.CTkLabel(main_frame, text="Name *").pack(anchor="w", pady=(0, 5))
        self.name_entry = ctk.CTkEntry(main_frame, textvariable=self.name_var, width=300)
        self.name_entry.pack(fill="x", pady=(0, 15))

        # Email
        ctk.CTkLabel(main_frame, text="Email").pack(anchor="w", pady=(0, 5))
        self.email_entry = ctk.CTkEntry(main_frame, textvariable=self.email_var, width=300)
        self.email_entry.pack(fill="x", pady=(0, 15))

        # Codementor
        ctk.CTkLabel(main_frame, text="Codementor Username").pack(anchor="w", pady=(0, 5))
        self.codementor_entry = ctk.CTkEntry(main_frame, textvariable=self.codementor_var, width=300)
        self.codementor_entry.pack(fill="x", pady=(0, 15))

        # Platform
        ctk.CTkLabel(main_frame, text="Platform Preference").pack(anchor="w", pady=(0, 5))
        self.platform_combo = ctk.CTkComboBox(main_frame, values=["email", "codementor", "both"],
                                              variable=self.platform_var, width=300)
        self.platform_combo.pack(fill="x", pady=(0, 15))

        # Notes
        ctk.CTkLabel(main_frame, text="Notes").pack(anchor="w", pady=(0, 5))
        self.notes_text = ctk.CTkTextbox(main_frame, width=300, height=100, font=ctk.CTkFont(family="Segoe UI Emoji", size=12))
        self.notes_text.pack(fill="x", pady=(0, 20))

        # Bind emoji processing to notes
        self.notes_text.bind('<KeyRelease>', self.process_emojis_realtime)

        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(button_frame, text="Cancel", command=self.cancel, width=100).pack(side="right", padx=(10, 0))
        ctk.CTkButton(button_frame, text="Save", command=self.save, width=100).pack(side="right")

    def load_contact_data(self):
        """Load existing contact data."""
        if not self.contact:
            return

        self.name_var.set(self.contact.name or "")
        self.email_var.set(self.contact.email or "")
        self.codementor_var.set(self.contact.codementor_username or "")
        self.platform_var.set(self.contact.platform_preference or "email")
        self.notes_text.insert("1.0", with_surrogates(self.contact.notes or ""))

    def save(self):
        """Save the contact."""
        if not self.name_var.get().strip():
            tk.messagebox.showerror("Error", "Name is required.")
            return

        try:
            db = Session(engine)

            if self.contact:
                # Update existing contact
                self.contact.name = self.name_var.get().strip()
                self.contact.email = self.email_var.get().strip() or None
                self.contact.codementor_username = self.codementor_var.get().strip() or None
                self.contact.platform_preference = self.platform_var.get()
                self.contact.notes = self.notes_text.get("1.0", "end-1c").strip() or None
                self.contact.updated_at = datetime.now(timezone.utc)
            else:
                # Create new contact
                contact = Contact(
                    name=self.name_var.get().strip(),
                    email=self.email_var.get().strip() or None,
                    codementor_username=self.codementor_var.get().strip() or None,
                    platform_preference=self.platform_var.get(),
                    notes=self.notes_text.get("1.0", "end-1c").strip() or None
                )
                db.add(contact)

            db.commit()
            db.close()

            self.result = True
            self.destroy()

        except Exception as e:
            tk.messagebox.showerror("Database Error", f"Failed to save contact: {str(e)}")

    def cancel(self):
        """Cancel the dialog."""
        self.result = False
        self.destroy()


class FollowupperApp(ctk.CTk):
    """Main application."""

    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Followupper - Automated Follow-up Manager")
        self.geometry("1000x700")
        self.minsize(800, 600)

        # Configure CustomTkinter
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Run migrations
        self.run_migrations()

        # Setup UI
        self.setup_ui()
        self.load_contacts()

    def run_migrations(self):
        """Run database migrations."""
        try:
            from alembic import command
            from alembic.config import Config
            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
            print("Database migrations completed successfully")
        except Exception as e:
            print(f"Error running migrations: {e}")
            # Create tables directly if migrations fail
            Base.metadata.create_all(bind=engine)
            print("Created database tables directly")

    def setup_ui(self):
        """Set up the main UI."""
        # Main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab view
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Add tabs
        self.contacts_tab = self.tabview.add("👥 Contacts")
        self.templates_tab = self.tabview.add("📝 Templates")
        self.schedule_tab = self.tabview.add("📅 Schedule")
        self.settings_tab = self.tabview.add("⚙️ Settings")

        # Status bar (setup before tabs)
        self.status_var = tk.StringVar(value="Ready")
        status_label = ctk.CTkLabel(self.main_frame, textvariable=self.status_var)
        status_label.pack(side="bottom", pady=5)

        # Setup each tab
        self.setup_contacts_tab()
        self.setup_templates_tab()
        self.setup_schedule_tab()
        self.setup_settings_tab()

    def setup_contacts_tab(self):
        """Set up the contacts tab."""
        # Header
        header_frame = ctk.CTkFrame(self.contacts_tab)
        header_frame.pack(fill="x", padx=10, pady=10)

        title = ctk.CTkLabel(header_frame, text="👥 Contacts", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(side="left", padx=20, pady=15)

        # Search and add button
        search_frame = ctk.CTkFrame(header_frame)
        search_frame.pack(side="right", padx=20, pady=15)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.search_contacts)
        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search contacts...",
                                    textvariable=self.search_var, width=200)
        search_entry.pack(side="left", padx=(0, 10))

        add_button = ctk.CTkButton(search_frame, text="Add Contact", command=self.add_contact, width=120)
        add_button.pack(side="left")

        # Contacts table
        table_frame = ctk.CTkFrame(self.contacts_tab)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Create treeview
        columns = ("ID", "Name", "Email", "Platform", "Status", "Actions")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Platform", text="Platform")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Actions", text="Actions")

        self.tree.column("ID", width=50)
        self.tree.column("Name", width=200)
        self.tree.column("Email", width=200)
        self.tree.column("Platform", width=100)
        self.tree.column("Status", width=80)
        self.tree.column("Actions", width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        self.tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        # Bind double-click event
        self.tree.bind("<Double-1>", self.edit_contact)

    def setup_templates_tab(self):
        """Set up the templates tab."""
        # Header
        header_frame = ctk.CTkFrame(self.templates_tab)
        header_frame.pack(fill="x", padx=10, pady=10)

        title = ctk.CTkLabel(header_frame, text="📝 Message Templates", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(side="left", padx=20, pady=15)

        # Add template button
        add_button = ctk.CTkButton(header_frame, text="Add Template", command=self.add_template, width=120)
        add_button.pack(side="right", padx=20, pady=15)

        # Templates table
        table_frame = ctk.CTkFrame(self.templates_tab)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Create treeview for templates
        columns = ("ID", "Name", "Subject", "Created")
        self.templates_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Configure columns
        self.templates_tree.heading("ID", text="ID")
        self.templates_tree.heading("Name", text="Name")
        self.templates_tree.heading("Subject", text="Subject")
        self.templates_tree.heading("Created", text="Created")

        self.templates_tree.column("ID", width=50)
        self.templates_tree.column("Name", width=250)
        self.templates_tree.column("Subject", width=400)
        self.templates_tree.column("Created", width=120)

        # Scrollbar
        templates_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.templates_tree.yview)
        self.templates_tree.configure(yscrollcommand=templates_scrollbar.set)

        # Pack treeview and scrollbar
        self.templates_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        templates_scrollbar.pack(side="right", fill="y", pady=10)

        # Bind double-click event
        self.templates_tree.bind("<Double-1>", self.edit_template)

        # Load templates
        self.load_templates()

    def setup_schedule_tab(self):
        """Set up the schedule tab."""
        # Header
        header_frame = ctk.CTkFrame(self.schedule_tab)
        header_frame.pack(fill="x", padx=10, pady=10)

        title = ctk.CTkLabel(header_frame, text="📅 Scheduled Follow-ups", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(side="left", padx=20, pady=15)

        # Refresh button
        refresh_button = ctk.CTkButton(header_frame, text="Refresh", command=self.load_schedule, width=120)
        refresh_button.pack(side="right", padx=20, pady=15)

        # Schedule table
        table_frame = ctk.CTkFrame(self.schedule_tab)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Create treeview for schedule
        columns = ("ID", "Contact", "Template", "Scheduled Time", "Status")
        self.schedule_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Configure columns
        self.schedule_tree.heading("ID", text="ID")
        self.schedule_tree.heading("Contact", text="Contact")
        self.schedule_tree.heading("Template", text="Template")
        self.schedule_tree.heading("Scheduled Time", text="Scheduled Time")
        self.schedule_tree.heading("Status", text="Status")

        self.schedule_tree.column("ID", width=50)
        self.schedule_tree.column("Contact", width=200)
        self.schedule_tree.column("Template", width=200)
        self.schedule_tree.column("Scheduled Time", width=150)
        self.schedule_tree.column("Status", width=100)

        # Scrollbar
        schedule_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.schedule_tree.yview)
        self.schedule_tree.configure(yscrollcommand=schedule_scrollbar.set)

        # Pack treeview and scrollbar
        self.schedule_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        schedule_scrollbar.pack(side="right", fill="y", pady=10)

        # Load schedule
        self.load_schedule()

    def setup_settings_tab(self):
        """Set up the settings tab."""
        # Header
        header_frame = ctk.CTkFrame(self.settings_tab)
        header_frame.pack(fill="x", padx=10, pady=10)

        title = ctk.CTkLabel(header_frame, text="⚙️ Settings", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(side="left", padx=20, pady=15)

        # Settings content
        settings_frame = ctk.CTkFrame(self.settings_tab)
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Database section
        db_frame = ctk.CTkFrame(settings_frame)
        db_frame.pack(fill="x", padx=10, pady=10)

        db_title = ctk.CTkLabel(db_frame, text="Database", font=ctk.CTkFont(size=18, weight="bold"))
        db_title.pack(anchor="w", padx=20, pady=(20, 10))

        # Database status
        self.db_status_var = tk.StringVar(value="Connected")
        db_status = ctk.CTkLabel(db_frame, textvariable=self.db_status_var)
        db_status.pack(anchor="w", padx=20, pady=(0, 10))

        # Platform credentials section
        creds_frame = ctk.CTkFrame(settings_frame)
        creds_frame.pack(fill="x", padx=10, pady=10)

        creds_title = ctk.CTkLabel(creds_frame, text="Platform Credentials", font=ctk.CTkFont(size=18, weight="bold"))
        creds_title.pack(anchor="w", padx=20, pady=(20, 10))

        # Gmail credentials
        gmail_frame = ctk.CTkFrame(creds_frame)
        gmail_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(gmail_frame, text="Gmail:").pack(anchor="w", padx=10, pady=5)
        self.gmail_email = ctk.CTkEntry(gmail_frame, placeholder_text="Gmail address", width=300)
        self.gmail_email.pack(anchor="w", padx=10, pady=5)

        self.gmail_password = ctk.CTkEntry(gmail_frame, placeholder_text="App password", width=300, show="*")
        self.gmail_password.pack(anchor="w", padx=10, pady=5)

        # Codementor credentials
        codementor_frame = ctk.CTkFrame(creds_frame)
        codementor_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(codementor_frame, text="Codementor:").pack(anchor="w", padx=10, pady=5)
        self.codementor_token = ctk.CTkEntry(codementor_frame, placeholder_text="API token", width=300)
        self.codementor_token.pack(anchor="w", padx=10, pady=5)

        # Save credentials button
        save_creds_button = ctk.CTkButton(creds_frame, text="Save Credentials", command=self.save_credentials, width=150)
        save_creds_button.pack(anchor="w", padx=20, pady=10)

    def load_contacts(self):
        """Load contacts from database."""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)

            db = Session(engine)
            contacts = db.query(Contact).order_by(Contact.name).all()

            for contact in contacts:
                status = "Active" if contact.is_active else "Inactive"
                self.tree.insert("", "end", values=(
                    contact.id,
                    contact.name,
                    contact.email or "",
                    contact.platform_preference or "email",
                    status,
                    "Edit"
                ))

            db.close()
            self.status_var.set(f"Loaded {len(contacts)} contacts")

        except Exception as e:
            self.status_var.set(f"Error loading contacts: {str(e)}")
            print(f"Error loading contacts: {e}")

    def search_contacts(self, *args):
        """Search contacts."""
        search_text = self.search_var.get().lower()

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            db = Session(engine)
            contacts = db.query(Contact).order_by(Contact.name).all()

            for contact in contacts:
                if (search_text in (contact.name or "").lower() or
                    search_text in (contact.email or "").lower() or
                        search_text in (contact.notes or "").lower()):

                    status = "Active" if contact.is_active else "Inactive"
                    self.tree.insert("", "end", values=(
                        contact.id,
                        contact.name,
                        contact.email or "",
                        contact.platform_preference or "email",
                        status,
                        "Edit"
                    ))

            db.close()

        except Exception as e:
            print(f"Error searching contacts: {e}")

    def add_contact(self):
        """Add a new contact."""
        dialog = ContactDialog(self)
        self.wait_window(dialog)

        if dialog.result:
            self.load_contacts()

    def edit_contact(self, event):
        """Edit a contact."""
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        contact_id = item['values'][0]

        try:
            db = Session(engine)
            contact = db.query(Contact).filter(Contact.id == contact_id).first()
            db.close()

            if contact:
                dialog = ContactDialog(self, contact)
                self.wait_window(dialog)

                if dialog.result:
                    self.load_contacts()

        except Exception as e:
            print(f"Error editing contact: {e}")

    def load_templates(self):
        """Load templates from database."""
        try:
            # Clear existing items
            for item in self.templates_tree.get_children():
                self.templates_tree.delete(item)

            db = Session(engine)
            templates = db.query(MessageTemplate).order_by(MessageTemplate.name).all()

            for template in templates:
                created_date = template.created_at.strftime("%Y-%m-%d") if template.created_at else "Unknown"
                self.templates_tree.insert("", "end", values=(
                    template.id,
                    template.name,
                    template.subject or "",
                    created_date
                ))

            db.close()
            self.status_var.set(f"Loaded {len(templates)} templates")

        except Exception as e:
            self.status_var.set(f"Error loading templates: {str(e)}")
            print(f"Error loading templates: {e}")

    def load_schedule(self):
        """Load scheduled follow-ups from database."""
        try:
            # Clear existing items
            for item in self.schedule_tree.get_children():
                self.schedule_tree.delete(item)

            db = Session(engine)
            followups = db.query(ScheduledFollowup).order_by(ScheduledFollowup.scheduled_date).all()

            for followup in followups:
                # Get contact name
                contact = db.query(Contact).filter(Contact.id == followup.contact_id).first()
                contact_name = contact.name if contact else "Unknown"

                # Get template name
                template = db.query(MessageTemplate).filter(MessageTemplate.id == followup.template_id).first()
                template_name = template.name if template else "Unknown"

                scheduled_time = followup.scheduled_date.strftime("%Y-%m-%d %H:%M") if followup.scheduled_date else "Unknown"

                self.schedule_tree.insert("", "end", values=(
                    followup.id,
                    contact_name,
                    template_name,
                    scheduled_time,
                    followup.status or "pending"
                ))

            db.close()
            self.status_var.set(f"Loaded {len(followups)} scheduled follow-ups")

        except Exception as e:
            self.status_var.set(f"Error loading schedule: {str(e)}")
            print(f"Error loading schedule: {e}")

    def add_template(self):
        """Add a new template."""
        # Create template dialog
        dialog = TemplateDialog(self)
        self.wait_window(dialog)

        if dialog.result:
            self.load_templates()

    def edit_template(self, event):
        """Edit a template."""
        selection = self.templates_tree.selection()
        if not selection:
            return

        item = self.templates_tree.item(selection[0])
        template_id = item['values'][0]

        try:
            db = Session(engine)
            template = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
            db.close()

            if template:
                dialog = TemplateDialog(self, template)
                self.wait_window(dialog)

                if dialog.result:
                    self.load_templates()

        except Exception as e:
            print(f"Error editing template: {e}")

    def save_credentials(self):
        """Save platform credentials."""
        try:
            db = Session(engine)

            # Save Gmail credentials
            gmail_email = self.gmail_email.get()
            gmail_password = self.gmail_password.get()

            if gmail_email and gmail_password:
                gmail_creds = db.query(PlatformCredentials).filter(PlatformCredentials.platform == "gmail").first()
                if gmail_creds:
                    gmail_creds.credentials = f"{gmail_email}:{gmail_password}"
                    gmail_creds.updated_at = datetime.now(timezone.utc)
                else:
                    gmail_creds = PlatformCredentials(
                        platform="gmail",
                        credentials=f"{gmail_email}:{gmail_password}"
                    )
                    db.add(gmail_creds)

            # Save Codementor credentials
            codementor_token = self.codementor_token.get()

            if codementor_token:
                codementor_creds = db.query(PlatformCredentials).filter(PlatformCredentials.platform == "codementor").first()
                if codementor_creds:
                    codementor_creds.credentials = codementor_token
                    codementor_creds.updated_at = datetime.now(timezone.utc)
                else:
                    codementor_creds = PlatformCredentials(
                        platform="codementor",
                        credentials=codementor_token
                    )
                    db.add(codementor_creds)

            db.commit()
            db.close()

            self.status_var.set("Credentials saved successfully")
            messagebox.showinfo("Success", "Credentials saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save credentials: {str(e)}")


def main():
    """Main application entry point."""
    app = FollowupperApp()
    app.mainloop()


if __name__ == "__main__":
    main()
