# 🔐 SafeLogin - Secure Authentication & Dashboard Platform

SafeLogin is a modern Flask-based web application that combines secure user authentication with a user-friendly dashboard interface.

## 🌟 Key Features

### 🔒 Security & Authentication
- **Secure Password Storage** with `bcrypt` hashing
- **Two-Factor Authentication (2FA)** with Google Authenticator
- **Session Management** with secure, configurable sessions
- **Rate Limiting** to protect against brute-force attacks
- **SQLite Database** for efficient data storage

### 📊 Modern Dashboard
- **Responsive Design** inspired by Google and Apple
- **Dark/Light Mode** with local preference storage
- **Grid and List Views** for cards
- **Drag & Drop File Upload**
- **Image Gallery** with previews
- **File Management** for various formats (PDF, Word, etc.)

### 🤝 Collaboration
- **Card Sharing** with other users
- **Granular Permissions** (Read/Edit)
- **Email-based Sharing**
- **Secure Access Control**

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python Package Manager)
- Git

### Steps

1. **Clone Repository**
```bash
git clone https://github.com/your-user/safelogin.git
cd safelogin
```

2. **Create Virtual Environment**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS & Linux:
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Settings**
Customize `config.py` according to your needs:
```python
SECRET_KEY = "your-secret-key"
SESSION_TYPE = "filesystem"
RATE_LIMIT = "100 per day"
UPLOAD_FOLDER = "uploads"
```

5. **Start Application**
```bash
python app.py
```

🌐 **Access:** [`http://127.0.0.1:5000`](http://127.0.0.1:5000)

---

## 📁 Project Structure

```
SafeLogin/
├── database/              # Database files
│   └── users.db           # SQLite database
├── static/                # Static files
│   ├── style.css          # Base styling
│   ├── dashboard.css      # Dashboard-specific styling
│   ├── dashboard.js       # Dashboard functionality
│   ├── flash-message.js   # Flash messages
│   └── password-check.js  # Password validation
├── templates/             # HTML templates
│   ├── login.html         # Login page
│   ├── register.html      # Registration
│   ├── 2fa.html           # 2FA verification
│   └── dashboard.html     # Main dashboard
├── uploads/               # Uploaded files
├── utils/                 # Helper functions
│   ├── database.py        # Database connection
│   └── security.py        # Security functions
├── app.py                 # Main application
├── config.py              # Configuration
└── requirements.txt       # Dependencies
```

## 💡 Feature Details

### Dashboard
1. **Card Management**
   - Create, edit, and delete cards
   - Add titles and descriptions
   - Upload files and images
   - Switch between grid and list views

2. **File Upload**
   - Drag & drop support
   - Multiple file upload
   - Image previews
   - Support for various file formats

3. **Sharing Features**
   - Share cards via email
   - Grant read or edit permissions
   - File-level access control

4. **User Interface**
   - Responsive design
   - Dark/Light mode
   - Intuitive navigation
   - Modern icons and animations

### Security
1. **Authentication**
   - Multi-step login process
   - 2FA with Google Authenticator
   - Secure password storage

2. **Access Control**
   - Role-based permissions
   - Secure session management
   - Rate limiting for API endpoints

3. **Data Security**
   - Encrypted file transfer
   - Secure data storage
   - Protected file sharing

## 🛠 API Endpoints

### Cards
- `POST /api/cards` - Create new card
- `PUT /api/cards/<id>` - Update card
- `DELETE /api/cards/<id>` - Delete card
- `POST /api/cards/<id>/files` - Upload files
- `POST /api/cards/<id>/share` - Share card

### Authentication
- `POST /login` - Login
- `POST /register` - Registration
- `POST /verify-2fa` - 2FA verification
- `GET /logout` - Logout

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

## 📜 License

This project is licensed under the MIT License.

---

## 🆘 Support

For questions or issues:
1. Create GitHub issues
2. Consult documentation
3. Submit pull requests for improvements
