# 🔐 WindCloud - Secure Cloud Storage & Dashboard Platform

WindCloud is a modern Flask-based web application that provides secure file storage, sharing capabilities, and an intuitive dashboard interface with advanced authentication features.

## 🌟 Key Features

### 🔒 Security & Authentication
- **Secure Password Storage** with `bcrypt` hashing
- **Two-Factor Authentication (2FA)** with Google Authenticator
- **Session Management** with secure, configurable sessions
- **Rate Limiting** to protect against brute-force attacks
- **SQLite Database** for efficient data storage
- **HTTPS Support** with secure cookie handling
- **Cross-Site Request Forgery (CSRF) Protection**
- **Input Validation & Sanitization**

### 📊 Modern Dashboard
- **Responsive Design** inspired by Google and Apple
- **Dark/Light Mode** with local preference storage
- **Grid and List Views** for cards
- **Drag & Drop File Upload**
- **Image Gallery** with previews
- **File Management** for various formats (PDF, Word, etc.)
- **Real-time Updates**
- **Search & Filter Capabilities**

### 🤝 Collaboration
- **Card Sharing** with other users
- **Granular Permissions** (Read/Edit)
- **Email-based Sharing**
- **Secure Access Control**
- **Activity Tracking**
- **Version History**

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python Package Manager)
- Git
- SQLite3
- Modern web browser with JavaScript enabled

### Steps

1. **Clone Repository**
```bash
git clone https://github.com/your-user/windcloud.git
cd windcloud
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
Create a `.env` file in the root directory and customize your settings:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secure-secret-key
SESSION_TYPE=filesystem
RATE_LIMIT=100/day
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB max file size
```

Or modify `config.py` directly:
```python
SECRET_KEY = "your-secure-secret-key"
SESSION_TYPE = "filesystem"
RATE_LIMIT = "100 per day"
UPLOAD_FOLDER = "uploads"
```

5. **Initialize Database**
```bash
flask init-db
```

6. **Start Application**
```bash
python app.py
```

🌐 **Access:** [`http://127.0.0.1:5000`](http://127.0.0.1:5000)

---

## 📁 Project Structure

```
WindCloud/
├── database/               # Database files
│   └── users.db            # SQLite database
├── static/                 # Static files
│   ├── style.css           # Base styling
│   ├── dashboard.css       # Dashboard-specific styling
│   ├── dashboard.js        # Dashboard functionality
│   ├── flash-message.js    # Flash messages
│   └── password-check.js   # Password validation
├── templates/              # HTML templates
│   ├── login.html          # Login page
│   ├── register.html       # Registration
│   ├── 2fa.html            # 2FA verification
│   └── dashboard.html      # Main dashboard
├── uploads/                # Uploaded files
├── utils/                  # Helper functions
│   ├── database.py         # Database connection
│   └── security.py         # Security functions
├── app.py                  # Main application
├── config.py               # Configuration
└── requirements.txt        # Dependencies

## 💡 Feature Details

### Dashboard
1. **Card Management**
   - Create, edit, and delete cards
   - Add titles and descriptions
   - Upload files and images
   - Switch between grid and list views
   - Sort and filter capabilities
   - Bulk operations support

2. **File Upload**
   - Drag & drop support
   - Multiple file upload
   - Image previews
   - Support for various file formats
   - Progress indicators
   - File validation
   - Automatic file type detection

3. **Sharing Features**
   - Share cards
   - Grant read or edit permissions
   - File-level access control

4. **User Interface**
   - Responsive design
   - Dark/Light mode
   - Intuitive navigation
   - Modern icons and animations
   - Keyboard shortcuts
   - Accessibility features
   - Touch-friendly controls

### Security
1. **Authentication**
   - Multi-step login process
   - 2FA with Google Authenticator
   - Secure password storage
   - Password strength requirements
   - Account lockout protection
   - Login attempt monitoring

2. **Access Control**
   - Secure session management
   - Rate limiting for API endpoints
   - IP-based restrictions

3. **Data Security**
   - Encrypted file transfer
   - Secure data storage
   - Protected file sharing
   - Data backup
   - File integrity checks
   - Secure file deletion

## 🛠 API Endpoints

### Authentication
- `POST /login` - User login
  - Parameters: `email`, `password`
  - Returns: Session token
- `POST /register` - New user registration
  - Parameters: `username`, `email`, `password`
- `POST /verify-2fa` - 2FA verification
  - Parameters: `token`
- `GET /logout` - User logout

### Cards
- `POST /api/cards` - Create new card
  - Parameters: `title`, `description`
- `PUT /api/cards/<id>` - Update card
  - Parameters: `title`, `description`
- `DELETE /api/cards/<id>` - Delete card
- `POST /api/cards/<id>/files` - Upload files
  - Parameters: `files[]`
- `POST /api/cards/<id>/share` - Share card
  - Parameters: `email`, `permission_level`

## 🧪 Testing (in Work)

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_auth.py

# Run with coverage report
coverage run -m pytest
coverage report
```

### Test Structure
- `tests/`
  - `test_auth.py` - Authentication tests
  - `test_cards.py` - Card management tests
  - `test_files.py` - File upload tests
  - `test_api.py` - API endpoint tests

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the Repository**
   - Create your own fork of the code
   - Clone the fork locally

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Write your code
   - Add tests if applicable
   - Update documentation

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add your meaningful commit message"
   ```

5. **Push to Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Submit Pull Request**
   - Create PR from your fork to our main branch
   - Describe your changes in detail
   - Reference any related issues

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add comments for complex logic
- Keep functions focused and small

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 🆘 Support & Troubleshooting

### Common Issues

1. **Database Errors**
   - Ensure SQLite3 is installed
   - Check database permissions
   - Verify database path

2. **Upload Issues**
   - Check file size limits
   - Verify upload directory permissions
   - Ensure proper file types

3. **Authentication Problems**
   - Clear browser cache
   - Check 2FA setup
   - Verify email configuration

### Getting Help

1. **Documentation**
   - Review [FAQ](faq)
   - Search existing issues

2. **Community Support**
   - Create GitHub issues
   - Check Stack Overflow tags

3. **Contributing**
   - Submit bug reports
   - Propose new features
   - Share improvements

## 📚 Additional Resources

- [Security Guidelines](security)
- **Coming Soon**

---

## 🔄 Version History

Built with ❤️ by Marsgame
