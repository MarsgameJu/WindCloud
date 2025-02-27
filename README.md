# 🔐 WindCloud - Secure Cloud Storage & Dashboard Platform

WindCloud is a modern Flask-based web application built for secure file storage, efficient sharing, and an interactive dashboard experience. With advanced authentication features including two-factor authentication (2FA), a flexible card system, and intuitive file management, WindCloud is designed for both individual users and collaborative teams.

---

## 🌟 Key Features

### Security & Authentication
- **Secure Password Storage:** Uses bcrypt for hashed passwords.
- **Two-Factor Authentication (2FA):** Integrated TOTP via Google Authenticator. Scan the QR code during registration and login.
- **Session Management & CSRF Protection:** Secure sessions and tokens.
- **Rate Limiting:** Prevents brute-force attacks.
- **Input Validation & Sanitization:** Ensures data integrity.

### Modern Dashboard
- **Responsive UI:** Designed with both grid and list views.
- **Dark/Light Mode:** User preference stored locally.
- **Drag & Drop File Upload:** Supports multiple file types and image previews.
- **Interactive Card System:** Create, edit, delete, and share cards.
- **Real-Time Updates & Search:** Quickly filter and sort your cards.

### File Management & Sharing
- **File & Image Galleries:** View and manage files via dedicated sections.
- **Granular Sharing Options:** Share cards with read-only or edit permissions.
- **Secure File Serving:** Files are stored and served securely from the uploads directory.

---

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip
- Git
- SQLite3

### Setup Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/MarsgameJu/WindCloud.git
   cd WindCloud
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**
   Create a `.env` file and update `config.py` with your settings:
   ```env
   MAIL_SERVER=smtp.example.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@example.com
   MAIL_PASSWORD=your-email-password
   ```
   [How to Create the App-password](https://support.google.com/accounts/answer/185833?hl=en)
   
   Alternatively, modify `config.py` accordingly.

5. **Database Initialization**
   The application automatically creates necessary tables. For a fresh start, remove existing databases and run:
   ```bash
   python app.py
   ```

6. **Start the Application**
   ```bash
   python app.py
   ```
   Visit [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📁 Project Structure

```
WindCloud/
├── .github/                # Holds issue templates
├── database/               # SQLite database and schema files
├── static/                 # Static assets: stylesheets, scripts
│   ├── assets/             # Images for Landing Page
│   ├── style.css           # Global styles
│   ├── dashboard.css       # Dashboard-specific styling
│   ├── script.js           # General JS functions
│   ├── dashboard.js        # Dashboard interactivity (cards, modals, uploads)
│   ├── flash-message.js    # Flash messages handler
│   ├── password-check.js   # Password validation and strength checking
│   ├── index.css           # Sytle for index.html
│   └── index.html          # Landing page
├── templates/              # Jinja2 HTML templates
│   ├── login.html          # User login
│   ├── register.html       # User registration
│   ├── 2fa.html            # Two-factor authentication
│   └── dashboard.html      # Main dashboard with card system
├── uploads/                # User-uploaded files
├── utils/                  # Helper functions for database & security operations
│   ├── database.py         # Strucure and Init Database
│   └── security.py         # ensures securoty for Webaplication
├── app.py                  # Main Flask application
├── config.py               # App configuration settings
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## 📜 API Endpoints

### Authentication
- **POST /login**
  - Parameters: `email`, `password`
  - Flow: Validates credentials and proceeds to 2FA.
- **POST /register**
  - Parameters: `username`, `email`, `password`, `confirm-password`
  - Flow: Registers user and prompts for 2FA setup.
- **POST /verify-2fa**
  - Parameters: `code`
  - Flow: Validates the TOTP code.

### Cards Management
- **POST /api/cards**
  - Payload: `title`, `description`
  - Creates a new card.
- **PUT /api/cards/<id>**
  - Payload: `title`, `description`
  - Updates an existing card. Requires owner or 'write' permission.
- **DELETE /api/cards/<id>**
  - Deletes the specified card. Associated files are also removed.

### File Handling
- **POST /api/cards/<id>/files**
  - Multipart form data for file(s).
  - Supports drag & drop file uploads.
- **DELETE /api/cards/<card_id>/files/<file_id>**
  - Deletes a file from a card.

### Card Sharing
- **POST /api/cards/<id>/share**
  - Payload: `email`, `permission` (read/write)
  - Grants the specified user permission to the card.

---


## 🤝 Contributing

We welcome enhancements and bug fixes!

1. **Fork the Repository**
2. **Create a Feature/Issue Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make Changes & Add Tests**
4. **Commit & Push**
   ```bash
   git add .
   git commit -m "Describe your change"
   git push origin feature/your-feature-name
   ```
5. **Submit a Pull Request**

Please follow PEP 8 guidelines and write clear commit messages.

---

## 📜 Other important things

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
- [Code of Conduct](info_doc/CODE_OF_CONDUCT.md)
- [Contributing Guidelines](info_doc/CONTRIBUTING.md)
- [License](info_doc/LICENSE)
- [Security Policy](info_doc/SECURITY.md)
- [Changelog](info_doc/CHANGELOG.md)
- [HowTo Email PW](https://support.google.com/accounts/answer/185833?hl=en)


---

## 🆘 Support & Documentation

- **FAQ & Issues:** Check our GitHub issues or discussions for common problems.
- **Contact:** Raise an issue for bug reports or feature requests.
- **Documentation:** More detailed guides and API references are coming soon.

---

Built by Marsgame. Enjoy a secure and seamless cloud storage experience!
