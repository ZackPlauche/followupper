# Followupper

**Automated follow-up application for managing client communications across multiple platforms.**

Followupper is a desktop application that automates follow-up communications with clients across Gmail, Codementor, and other platforms. It manages contact profiles, schedules automated messages, and tracks communication history.

## ✨ Features

### 🏗️ **Core Functionality**
- **Contact Management**: Add, edit, and organize client contacts with custom follow-up frequencies
- **Message Templates**: Create reusable message templates for different platforms
- **Automated Scheduling**: Schedule follow-ups with configurable intervals using APScheduler
- **Multi-Platform Support**: Gmail and Codementor integration (extensible to other platforms)
- **Background Operation**: Runs as Windows service with system tray support

### 📊 **Advanced Features**
- **Real-time Dashboard**: Live statistics and status monitoring
- **Failed Message Recovery**: Automatic retry mechanisms for failed messages
- **Secure Credential Storage**: Encrypted storage of platform credentials
- **Database Migrations**: Alembic-powered schema management
- **Professional GUI**: Modern PySide6 interface with tabbed navigation

## 🚀 **Quick Start**

### Prerequisites
- Python 3.13 or higher
- `uv` package manager (recommended) or `pip`

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd followupper
```

2. **Install dependencies:**
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

3. **Run the application:**
```bash
# Using uv
uv run python main.py

# Or directly
python main.py
```

## 📱 **Application Interface**

### **Contacts Tab**
- Add/edit client contacts with custom follow-up frequencies
- Platform preferences (Email, Codementor, or Both)
- Contact notes and communication history
- Bulk operations and filtering

### **Templates Tab**
- Create message templates for different platforms
- Variable substitution (e.g., `{name}`, `{email}`)
- Default template management
- Template preview and testing

### **Schedule Tab**
- View all scheduled follow-ups
- Filter by status (Pending, Sent, Failed, Overdue)
- Retry failed messages
- Cancel pending follow-ups
- Real-time status updates

### **Settings Tab**
- **Credentials**: Secure storage of Gmail and Codementor API credentials
- **General Settings**: Application preferences and notifications
- **About**: Version information and feature overview

## 🔧 **Configuration**

### **Database**
The application automatically:
- Creates SQLite database (`followupper.db`)
- Runs database migrations
- Sets up all necessary tables and relationships

### **Credentials Setup**
1. Navigate to **Settings > Credentials**
2. Enter your Gmail OAuth credentials:
   - Client ID
   - Client Secret  
   - Refresh Token
3. Enter your Codementor API key
4. Test connections to verify setup

### **Platform Integration**
- **Gmail**: Uses OAuth2 for secure email sending
- **Codementor**: API key-based authentication
- **Extensible**: Easy to add new platforms

## 🏗️ **Architecture**

### **Tech Stack**
- **GUI**: PySide6 (Qt for Python)
- **Database**: SQLAlchemy with SQLite
- **Migrations**: Alembic
- **Scheduling**: APScheduler
- **Encryption**: Cryptography (Fernet)
- **Package Management**: uv

### **Project Structure**
```
followupper/
├── src/
│   ├── models/          # Database models
│   ├── gui/             # GUI components
│   ├── scheduler/       # Background scheduling
│   └── app.py           # Main application
├── migrations/          # Database migrations
├── main.py              # Entry point
└── requirements.txt     # Dependencies
```

## 🔄 **Database Schema**

### **Core Tables**
- **contacts**: Client information and follow-up preferences
- **message_templates**: Reusable message templates
- **scheduled_followups**: Automated message scheduling
- **platform_credentials**: Encrypted API credentials

### **Relationships**
- Contacts → Scheduled Follow-ups (One-to-Many)
- Templates → Scheduled Follow-ups (One-to-Many)
- Automatic foreign key management

## 🚀 **Advanced Usage**

### **Scheduling System**
- Automatic follow-up scheduling based on contact preferences
- Configurable retry mechanisms for failed messages
- Background job processing with APScheduler
- Real-time status monitoring

### **Message Templates**
- Variable substitution: `{name}`, `{email}`, `{platform}`
- Platform-specific templates (Email vs Codementor)
- Default template management
- Template preview and validation

### **Background Operation**
- Windows system tray integration
- Startup configuration
- Background message processing
- Error handling and recovery

## 🔗 **Integration Links**

- **Gmail Client**: [python-gmail](https://github.com/zackplauche/python-gmail)
- **Codementor API**: [codementorapi](https://github.com/zackplauche/codementorapi)

## 🛠️ **Development**

### **Running Migrations**
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

### **Database Management**
- Automatic migration on startup
- Fallback to direct table creation
- Version-controlled schema changes

## 📋 **Requirements Met**

✅ **Contact Management**: Full CRUD operations with custom follow-up frequencies  
✅ **Message Templates**: Reusable templates with variable substitution  
✅ **Automated Scheduling**: APScheduler-powered background processing  
✅ **Platform Integration**: Gmail and Codementor API support  
✅ **Error Recovery**: Failed message tracking and retry mechanisms  
✅ **Credential Security**: Encrypted storage of API credentials  
✅ **Background Operation**: Windows service and system tray support  
✅ **Professional GUI**: Modern PySide6 interface with real-time updates  

## 🎯 **Future Enhancements**

- **Additional Platforms**: Discord, WhatsApp, Messenger integration
- **Cloud Hosting**: Web-based version for remote access
- **Advanced Analytics**: Communication metrics and insights
- **Team Collaboration**: Multi-user support and permissions
- **API Integration**: REST API for external integrations

---

**Built with ❤️ for automated client communication management.**