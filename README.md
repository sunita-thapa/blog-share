# 📝 BlogSphere — Flask Blog & Portfolio Platform

A colourful, full-featured blog and personal portfolio platform built with Flask.
Created as a college assignment — beginner-friendly code with detailed comments throughout.

---

## ✨ Features

- **Blog System** — Create, edit, delete, and publish articles with categories, tags, and cover images
- **Portfolio Pages** — Public profile page showing projects, skills, and technologies
- **User Authentication** — Register, login, logout with secure password hashing
- **Dashboard** — Manage all your content from one place
- **CRUD Operations** — Full Create/Read/Update/Delete for Posts, Projects, Skills, and Technologies
- **Responsive Design** — Works on mobile, tablet, and desktop
- **Sky Blue + Crimson Theme** — Professional and eye-catching colour scheme

---

## 🗂️ Project Structure

```
blog_platform/
│
├── app.py                  ← Main Flask app (routes, models, logic)
├── requirements.txt        ← Python packages needed
├── README.md               ← This file
│
├── instance/
│   └── blog_platform.db    ← SQLite database (auto-created on first run)
│
├── static/
│   ├── css/
│   │   └── style.css       ← All custom styles
│   └── js/
│       └── main.js         ← JavaScript (form validation, animations, etc.)
│
└── templates/
    ├── base.html           ← Shared layout (navbar, footer, flash messages)
    ├── home.html           ← Landing page
    ├── blog.html           ← Blog archive / listing
    ├── post_detail.html    ← Single post view
    ├── portfolio.html      ← Public user portfolio
    ├── about.html          ← About page
    ├── contact.html        ← Contact form
    ├── privacy.html        ← Privacy policy
    ├── cookies.html        ← Cookie policy
    ├── register.html       ← Sign up form
    ├── login.html          ← Sign in form
    ├── dashboard.html      ← User dashboard
    ├── edit_profile.html   ← Profile editor
    ├── post_form.html      ← Create / edit post
    ├── project_form.html   ← Create / edit project
    ├── skill_form.html     ← Add / edit skill
    ├── tech_form.html      ← Add / edit technology
    ├── 404.html            ← Page not found
    └── 403.html            ← Access forbidden
```

---

## 🗄️ Database Tables

| Table         | Description                              |
|---------------|------------------------------------------|
| `users`       | Registered accounts (auth + profile)    |
| `posts`       | Blog articles with categories & tags    |
| `projects`    | Portfolio projects with links           |
| `skills`      | Named skills with proficiency %         |
| `technologies`| Tools & platforms with colour badges    |

---

## 🚀 How to Run

### 1. Install Python (3.10+ recommended)

### 2. Create a virtual environment (optional but recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python app.py
```

### 5. Open in browser
```
http://127.0.0.1:5000
```

### 6. Demo login
```
Username: admin
Password: admin123
```

---

## 🔐 Security Notes

- Passwords are **never stored in plain text** — hashed with Werkzeug's `generate_password_hash`
- Session management uses Flask's built-in session with a secret key
- All dashboard routes are protected with `@login_required`
- Users can only edit/delete their **own** content (ownership checks with `abort(403)`)

---

## 📚 Technologies Used

| Technology     | Purpose                        |
|----------------|--------------------------------|
| Flask          | Python web framework           |
| SQLAlchemy     | Database ORM                   |
| SQLite         | Database (file-based, no setup)|
| Jinja2         | HTML templating                |
| Bootstrap 5    | Responsive CSS framework       |
| Font Awesome   | Icons                          |
| Google Fonts   | Typography (Playfair + DM Sans)|
| Werkzeug       | Password hashing               |

---

## 💡 For Beginners

Every file has **detailed comments** explaining what each part does. Start by reading:
1. `app.py` — understand models and routes
2. `templates/base.html` — understand the shared layout
3. `static/css/style.css` — understand the visual theme
4. `static/js/main.js` — understand the interactive features

---

*Built with ❤️ using Flask — College Assignment Project*
