# Followupper

**Automated follow-up application for managing client communications across multiple platforms.**

Followupper is a web-based application that automates follow-up communications with clients across Gmail, Codementor, and other platforms. It manages contact profiles, creates automated campaigns, schedules messages, and tracks communication history.

## ✨ Features

### 🏗️ **Core Functionality**
- **Contact Management**: Add, edit, and organize client contacts with platform preferences
- **Campaign Management**: Create recurring or sequence campaigns with automated messaging
- **Message Templates**: Create reusable message templates with advanced variable substitution
- **Automated Scheduling**: Schedule follow-ups with configurable intervals (daily, weekly, monthly, quarterly, yearly, or custom)
- **Multi-Platform Support**: Gmail and Codementor integration with rate limiting
- **Bulk Operations**: Send bulk messages to multiple contacts with platform preferences

### 📊 **Advanced Campaign Features**
- **Recurring Campaigns**: Set up automated recurring messages with frequency controls
- **Sequence Campaigns**: Create multi-step message sequences with delays
- **Assignment Management**: 
  - Pause/resume individual assignments
  - Custom frequency per contact
  - Custom message overrides per contact
  - Edit next send date individually
  - Send messages immediately
  - Bulk edit status, frequency, message, and next send date
- **Test Messages**: Test campaign messages before sending
- **Live Preview**: Real-time preview of messages with template variables

### 🎨 **Template System**
- **Variable Substitution**: 
  - Contact variables: `{name}`, `{first_name}`, `{last_name}`, `{preferred_name}`, `{email}`, `{gender}`, `{codementor_username}`
  - Date variables: `{day}`, `{month}`, `{last_month}`, `{last_year}`
  - Campaign variables: `{frequency}`, `{frequency_days}`, `{season}`, `{holiday}`
- **Conditional Logic**:
  - Gender conditionals: `{if_male:text}`, `{if_female:text}`
  - Frequency conditionals: `{if_frequency_week:text}`, `{if_frequency_month:text}`, etc.
  - Seasonal conditionals: `{if_spring:text}`, `{if_summer:text}`, `{if_fall:text}`, `{if_winter:text}`
  - Holiday conditionals: `{if_christmas:text}`, `{if_halloween:text}`, `{if_thanksgiving:text}`, `{if_easter:text}`, `{if_newyear:text}`, `{if_holiday:text}`
  - Nested conditionals supported
- **Subject Templates**: Custom subject lines for recurring campaigns

### 🔧 **Technical Features**
- **Rate Limiting**: Configurable Codementor API rate limiting (concurrent sends and intervals)
- **Timezone Support**: Contact-based or campaign-based timezone handling
- **Failed Message Recovery**: Automatic retry mechanisms for failed messages
- **Secure Credential Storage**: Encrypted storage of platform credentials
- **Database Migrations**: Django-powered schema management
- **RESTful API**: Django REST Framework backend
- **Modern UI**: Nuxt 3 with Tailwind CSS, responsive design

## 🚀 **Quick Start**

### Prerequisites
- Python 3.13 or higher
- Node.js 18+ and npm/yarn
- `uv` package manager (recommended) or `pip`

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd followupper
```

2. **Backend Setup:**
```bash
# Using uv (recommended)
cd backend
uv sync

# Or using pip
pip install -r requirements.txt
```

3. **Frontend Setup:**
```bash
cd frontend
npm install
# or
yarn install
```

4. **Run the application:**

**Backend (Django):**
```bash
cd backend
# Using uv
uv run python manage.py runserver

# Or directly
python manage.py runserver
```

**Frontend (Nuxt 3):**
```bash
cd frontend
npm run dev
# or
yarn dev
```

The application will be available at `http://localhost:3000` (frontend) and `http://localhost:8000` (backend API).

## 📱 **Application Interface**

### **Contacts Page**
- Add/edit client contacts with platform preferences
- Filter contacts by platform, status, and search
- Bulk select and bulk operations (send messages, edit)
- Contact profile view with communication history
- Export contacts functionality

### **Templates Page**
- Create and manage message templates
- Live preview with template variable substitution
- Variable hints and conditional documentation
- Active/inactive template status
- Template testing

### **Campaigns Page**
- **Campaign Management**:
  - Create recurring or sequence campaigns
  - Edit campaign settings (frequency, send day/time, timezone)
  - Test campaign messages
  - Delete campaigns
  
- **Assignment Management**:
  - Add contacts to campaigns
  - View all assignments with status, frequency, next send date
  - Individual controls:
    - Pause/resume assignments
    - Edit frequency (with day/time selectors)
    - Edit next send date
    - Set custom message override
    - Send message immediately
  - Bulk operations:
    - Bulk select assignments
    - Bulk edit status, frequency, message, next send date
    - Bulk delete assignments
  - Visual indicators for paused assignments and custom messages

### **Bulk Message Editor**
- Send messages to multiple selected contacts
- Use contact's preferred platforms or manually select
- Template variable support with live preview
- Subject line support for email

## 🔧 **Configuration**

### **Database**
The application uses Django's ORM with SQLite (default) or PostgreSQL:
- Automatic migrations on startup
- Models: Contact, Campaign, CampaignAssignment, CampaignStep, MessageTemplate, Message, etc.

### **Credentials Setup**
1. Navigate to **Settings** (if available in UI)
2. Enter your Gmail OAuth credentials:
   - Client ID
   - Client Secret  
   - Refresh Token
3. Enter your Codementor API key
4. Configure rate limiting settings (max concurrent, send interval)

### **Platform Integration**
- **Gmail**: Uses OAuth2 for secure email sending
- **Codementor**: API key-based authentication with rate limiting
- **Extensible**: Easy to add new platforms

## 🏗️ **Architecture**

### **Tech Stack**
- **Backend**: Django 5.x with Django REST Framework
- **Frontend**: Nuxt 3 (Vue 3) with Tailwind CSS
- **Database**: SQLite (default) or PostgreSQL
- **Scheduling**: APScheduler for background message processing
- **Encryption**: Cryptography (Fernet) for credential storage
- **Package Management**: uv (backend), npm/yarn (frontend)

### **Project Structure**
```
followupper/
├── backend/
│   ├── followupper/
│   │   ├── models.py          # Database models
│   │   ├── views.py           # API views
│   │   ├── serializers.py     # DRF serializers
│   │   ├── scheduler.py       # Background scheduling
│   │   └── urls.py            # URL routing
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── pages/             # Page components
│   │   ├── components/         # Reusable components
│   │   ├── composables/        # Vue composables
│   │   └── layouts/            # Layout components
│   └── package.json
└── README.md
```

## 🔄 **Database Schema**

### **Core Models**
- **Contact**: Client information, platform preferences, communication history
- **Campaign**: Campaign configuration (recurring or sequence)
- **CampaignAssignment**: Links contacts to campaigns with custom settings
- **CampaignStep**: Steps for sequence campaigns
- **MessageTemplate**: Reusable message templates
- **Message**: Sent message history
- **PlatformCredentials**: Encrypted API credentials
- **UserSettings**: Application settings (rate limits, timezone, etc.)

### **Relationships**
- Contacts → Campaign Assignments (Many-to-Many through CampaignAssignment)
- Campaigns → Campaign Steps (One-to-Many)
- Campaigns → Campaign Assignments (One-to-Many)
- Contacts → Messages (One-to-Many)

## 🚀 **Advanced Usage**

### **Campaign Scheduling**
- **Recurring Campaigns**: 
  - Daily, weekly, monthly, quarterly, yearly, or custom intervals
  - Configurable send day (day of week for weekly, day of month for monthly/quarterly/yearly)
  - Configurable send time
  - Per-contact custom frequency overrides
  - Automatic next send date calculation
  
- **Sequence Campaigns**:
  - Multi-step message sequences
  - Configurable delays between steps
  - Automatic progression

### **Template Variables**
- **Contact Variables**: `{name}`, `{first_name}`, `{last_name}`, `{preferred_name}`, `{email}`, `{gender}`, `{codementor_username}`
- **Date Variables**: `{day}`, `{month}`, `{last_month}`, `{last_year}`
- **Campaign Variables**: `{frequency}`, `{frequency_days}`, `{season}`, `{holiday}`
- **Conditionals**: Support for gender, frequency, seasonal, and holiday-based conditionals with nesting

### **Rate Limiting**
- Configurable Codementor API rate limits
- Maximum concurrent sends
- Interval between sends
- Automatic queue management

### **Background Processing**
- APScheduler for scheduled message sending
- Automatic processing of due messages
- Failed message retry mechanisms
- Concurrent campaign support

## 🔗 **Integration Links**

- **Gmail Client**: [python-gmail](https://github.com/zackplauche/python-gmail)
- **Codementor API**: [codementorapi](https://github.com/zackplauche/codementorapi)

## 🛠️ **Development**

### **Backend Development**
```bash
cd backend
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Run development server
python manage.py runserver
```

### **Frontend Development**
```bash
cd frontend
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### **Database Management**
- Automatic migration on startup
- Django admin interface available at `/admin/`
- Version-controlled schema changes

## 📋 **Key Features Implemented**

✅ **Contact Management**: Full CRUD operations with platform preferences  
✅ **Campaign Management**: Recurring and sequence campaigns with full control  
✅ **Assignment Management**: Individual and bulk operations (pause, frequency, message, next send)  
✅ **Message Templates**: Advanced template system with variables and conditionals  
✅ **Bulk Messaging**: Send to multiple contacts with platform preferences  
✅ **Automated Scheduling**: APScheduler-powered background processing  
✅ **Platform Integration**: Gmail and Codementor API support with rate limiting  
✅ **Test Messages**: Test campaign messages before sending  
✅ **Live Previews**: Real-time preview of messages with template variables  
✅ **Error Recovery**: Failed message tracking and retry mechanisms  
✅ **Credential Security**: Encrypted storage of API credentials  
✅ **Modern UI**: Responsive Nuxt 3 interface with Tailwind CSS  

## 🎯 **Future Enhancements**

- **Additional Platforms**: Discord, WhatsApp, Messenger integration
- **Advanced Analytics**: Communication metrics and insights dashboard
- **Team Collaboration**: Multi-user support and permissions
- **API Documentation**: Swagger/OpenAPI documentation
- **Email Threading**: Reply-to message threading for Gmail
- **Campaign Analytics**: Open rates, engagement metrics
- **A/B Testing**: Test different message variations

---

**Built with ❤️ for automated client communication management.**
