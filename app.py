# ============================================================
# app.py - The heart of our Flask Blog Platform
# This is where everything starts! Think of this as the
# "main control room" of your website.
# ============================================================

from flask import Flask, render_template, redirect, url_for, flash, request, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import os

# ------------------------------------------------------------
# 1. CREATE THE FLASK APP
# Flask(__name__) tells Flask where to find templates & static files
# ------------------------------------------------------------
app = Flask(__name__)

# ------------------------------------------------------------
# 2. CONFIGURATION
# Secret key is needed for sessions & flash messages.
# Never share your secret key publicly!
# ------------------------------------------------------------
app.config['SECRET_KEY'] = 'your-super-secret-key-change-this-in-production'

# This sets up our SQLite database file location
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog_platform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Saves memory

# ------------------------------------------------------------
# 3. INITIALIZE THE DATABASE
# db is our "gateway" to talk to the database
# ------------------------------------------------------------
db = SQLAlchemy(app)


# ============================================================
# DATABASE MODELS (Tables)
# Each class = one table in our database
# Each variable inside = one column in that table
# ============================================================

class User(db.Model):
    """
    TABLE: users
    Stores all registered users.
    One user can have many posts, projects, skills, and technologies.
    """
    __tablename__ = 'users'

    id           = db.Column(db.Integer, primary_key=True)            # Auto ID
    username     = db.Column(db.String(80),  unique=True, nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    password     = db.Column(db.String(200), nullable=False)          # Stored as hash
    full_name    = db.Column(db.String(120), default='')
    bio          = db.Column(db.Text,        default='')
    avatar_url   = db.Column(db.String(300), default='')
    website      = db.Column(db.String(200), default='')
    github       = db.Column(db.String(200), default='')
    linkedin     = db.Column(db.String(200), default='')
    is_admin     = db.Column(db.Boolean,     default=False)
    created_at   = db.Column(db.DateTime,    default=datetime.utcnow)

    # Relationships: one user → many of each
    posts        = db.relationship('Post',       backref='author',   lazy=True, cascade='all, delete-orphan')
    projects     = db.relationship('Project',    backref='owner',    lazy=True, cascade='all, delete-orphan')
    skills       = db.relationship('Skill',      backref='owner',    lazy=True, cascade='all, delete-orphan')
    technologies = db.relationship('Technology', backref='owner',    lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    """
    TABLE: posts
    Stores blog articles/posts.
    Each post belongs to one user (author).
    """
    __tablename__ = 'posts'

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(200), nullable=False)
    slug         = db.Column(db.String(200), unique=True, nullable=False)  # URL-friendly title
    content      = db.Column(db.Text,        nullable=False)
    excerpt      = db.Column(db.String(300), default='')                   # Short summary
    category     = db.Column(db.String(80),  default='General')
    tags         = db.Column(db.String(200), default='')                   # Comma-separated
    cover_image  = db.Column(db.String(300), default='')
    is_published = db.Column(db.Boolean,     default=False)
    views        = db.Column(db.Integer,     default=0)
    created_at   = db.Column(db.DateTime,    default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id      = db.Column(db.Integer,     db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Post {self.title}>'

    def get_tags_list(self):
        """Helper: converts comma string → Python list"""
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def reading_time(self):
        """Estimate reading time (avg 200 words/min)"""
        words = len(self.content.split())
        minutes = max(1, round(words / 200))
        return f"{minutes} min read"


class Project(db.Model):
    """
    TABLE: projects
    Stores portfolio projects for each user.
    """
    __tablename__ = 'projects'

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(200), nullable=False)
    description  = db.Column(db.Text,        nullable=False)
    tech_stack   = db.Column(db.String(300), default='')    # e.g. "Python, Flask, JS"
    github_url   = db.Column(db.String(300), default='')
    live_url     = db.Column(db.String(300), default='')
    image_url    = db.Column(db.String(300), default='')
    is_featured  = db.Column(db.Boolean,     default=False)
    created_at   = db.Column(db.DateTime,    default=datetime.utcnow)
    user_id      = db.Column(db.Integer,     db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Project {self.title}>'


class Skill(db.Model):
    """
    TABLE: skills
    Stores skills (e.g. Python, Photoshop) for each user.
    """
    __tablename__ = 'skills'

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100), nullable=False)
    category     = db.Column(db.String(80),  default='General')  # e.g. Frontend, Backend
    proficiency  = db.Column(db.Integer,     default=75)         # 0–100 percentage
    icon         = db.Column(db.String(100), default='')         # Optional icon class
    created_at   = db.Column(db.DateTime,    default=datetime.utcnow)
    user_id      = db.Column(db.Integer,     db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Skill {self.name}>'


class Technology(db.Model):
    """
    TABLE: technologies
    Stores tools/technologies a user works with (e.g. Docker, VS Code).
    """
    __tablename__ = 'technologies'

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100), nullable=False)
    category     = db.Column(db.String(80),  default='Tool')   # e.g. DevOps, Database
    description  = db.Column(db.String(300), default='')
    badge_color  = db.Column(db.String(20),  default='#0ea5e9') # Hex colour for badge
    created_at   = db.Column(db.DateTime,    default=datetime.utcnow)
    user_id      = db.Column(db.Integer,     db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Technology {self.name}>'


# ============================================================
# HELPER: LOGIN REQUIRED DECORATOR
# Protects pages so only logged-in users can access them.
# Add @login_required above any route you want to protect.
# ============================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Returns the currently logged-in User object, or None."""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


def make_slug(title):
    """Converts 'My Cool Post' → 'my-cool-post' for clean URLs."""
    import re
    slug = title.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = re.sub(r'^-+|-+$', '', slug)
    return slug


# ============================================================
# PUBLIC ROUTES (anyone can visit)
# ============================================================

@app.route('/')
def home():
    """Home page — shows latest posts and a welcome message."""
    recent_posts  = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).limit(6).all()
    featured_post = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).first()
    total_posts   = Post.query.filter_by(is_published=True).count()
    total_users   = User.query.count()
    current_user  = get_current_user()
    return render_template('home.html',
                           recent_posts=recent_posts,
                           featured_post=featured_post,
                           total_posts=total_posts,
                           total_users=total_users,
                           current_user=current_user)


@app.route('/blog')
def blog():
    """Blog/Archive page — paginated list of all published posts."""
    page     = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search   = request.args.get('search', '')

    query = Post.query.filter_by(is_published=True)

    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Post.title.ilike(f'%{search}%'))

    posts       = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=9, error_out=False)
    categories  = db.session.query(Post.category).filter_by(is_published=True).distinct().all()
    current_user = get_current_user()

    return render_template('blog.html', posts=posts, categories=categories,
                           selected_category=category, search=search, current_user=current_user)


@app.route('/post/<slug>')
def post_detail(slug):
    """Individual post page."""
    post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()
    post.views += 1
    db.session.commit()

    related_posts = Post.query.filter_by(category=post.category, is_published=True)\
                              .filter(Post.id != post.id).limit(3).all()
    current_user  = get_current_user()
    return render_template('post_detail.html', post=post,
                           related_posts=related_posts, current_user=current_user)


@app.route('/portfolio/<username>')
def portfolio(username):
    """Public portfolio page for a specific user."""
    user         = User.query.filter_by(username=username).first_or_404()
    projects     = Project.query.filter_by(user_id=user.id).all()
    skills       = Skill.query.filter_by(user_id=user.id).all()
    technologies = Technology.query.filter_by(user_id=user.id).all()
    posts        = Post.query.filter_by(user_id=user.id, is_published=True)\
                             .order_by(Post.created_at.desc()).limit(3).all()
    current_user = get_current_user()

    # Group skills by category for organised display
    skill_categories = {}
    for skill in skills:
        skill_categories.setdefault(skill.category, []).append(skill)

    return render_template('portfolio.html', user=user, projects=projects,
                           skill_categories=skill_categories, technologies=technologies,
                           posts=posts, current_user=current_user)


@app.route('/about')
def about():
    """About page."""
    current_user = get_current_user()
    return render_template('about.html', current_user=current_user)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with a simple form."""
    current_user = get_current_user()
    if request.method == 'POST':
        name    = request.form.get('name', '').strip()
        email   = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        # Basic server-side validation
        if not name or not email or not message:
            flash('Please fill in all required fields.', 'danger')
        elif '@' not in email:
            flash('Please enter a valid email address.', 'danger')
        else:
            # In a real project you'd send an email here (e.g. Flask-Mail)
            flash(f'Thanks {name}! Your message has been received. We\'ll get back to you soon.', 'success')
            return redirect(url_for('contact'))

    return render_template('contact.html', current_user=current_user)


@app.route('/privacy')
def privacy():
    """Privacy Policy page."""
    current_user = get_current_user()
    return render_template('privacy.html', current_user=current_user)


@app.route('/cookies')
def cookies():
    """Cookie Policy page."""
    current_user = get_current_user()
    return render_template('cookies.html', current_user=current_user)


# ============================================================
# AUTH ROUTES (Register / Login / Logout)
# ============================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    current_user = get_current_user()

    if request.method == 'POST':
        username  = request.form.get('username', '').strip()
        email     = request.form.get('email', '').strip().lower()
        password  = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        full_name = request.form.get('full_name', '').strip()

        # ---- Validation ----
        errors = []
        if len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != password2:
            errors.append('Passwords do not match.')
        if User.query.filter_by(username=username).first():
            errors.append('Username already taken.')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')

        if errors:
            for e in errors:
                flash(e, 'danger')
        else:
            # Hash the password before saving — NEVER store plain-text passwords!
            hashed_pw = generate_password_hash(password)
            new_user  = User(username=username, email=email,
                             password=hashed_pw, full_name=full_name)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    current_user = get_current_user()

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()  # username or email
        password   = request.form.get('password', '')

        # Find user by username OR email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if user and check_password_hash(user.password, password):
            # Save user ID in session — this is how we "remember" who is logged in
            session['user_id']  = user.id
            session['username'] = user.username
            flash(f'Welcome back, {user.full_name or user.username}! 👋', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username/email or password.', 'danger')

    return render_template('login.html', current_user=current_user)


@app.route('/logout')
def logout():
    """Clear session and log out."""
    session.clear()
    flash('You have been logged out. See you soon!', 'info')
    return redirect(url_for('home'))


# ============================================================
# DASHBOARD ROUTES (login required)
# ============================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard — overview of all user content."""
    user         = get_current_user()
    posts        = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    projects     = Project.query.filter_by(user_id=user.id).all()
    skills       = Skill.query.filter_by(user_id=user.id).all()
    technologies = Technology.query.filter_by(user_id=user.id).all()

    stats = {
        'posts':        len(posts),
        'published':    sum(1 for p in posts if p.is_published),
        'drafts':       sum(1 for p in posts if not p.is_published),
        'projects':     len(projects),
        'skills':       len(skills),
        'technologies': len(technologies),
        'total_views':  sum(p.views for p in posts),
    }

    return render_template('dashboard.html', user=user, posts=posts,
                           projects=projects, skills=skills,
                           technologies=technologies, stats=stats,
                           current_user=user)


@app.route('/dashboard/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit profile information."""
    user = get_current_user()

    if request.method == 'POST':
        user.full_name  = request.form.get('full_name', '').strip()
        user.bio        = request.form.get('bio', '').strip()
        user.avatar_url = request.form.get('avatar_url', '').strip()
        user.website    = request.form.get('website', '').strip()
        user.github     = request.form.get('github', '').strip()
        user.linkedin   = request.form.get('linkedin', '').strip()

        # Change password if provided
        new_password = request.form.get('new_password', '')
        if new_password:
            if len(new_password) < 6:
                flash('New password must be at least 6 characters.', 'danger')
                return render_template('edit_profile.html', user=user, current_user=user)
            user.password = generate_password_hash(new_password)

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_profile.html', user=user, current_user=user)


# ---- POSTS CRUD ----

@app.route('/dashboard/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    """Create a new blog post."""
    user = get_current_user()

    if request.method == 'POST':
        title   = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        excerpt = request.form.get('excerpt', '').strip()
        category    = request.form.get('category', 'General')
        tags        = request.form.get('tags', '').strip()
        cover_image = request.form.get('cover_image', '').strip()
        publish     = request.form.get('publish') == 'on'

        if not title or not content:
            flash('Title and content are required.', 'danger')
        else:
            # Generate a unique slug from the title
            base_slug = make_slug(title)
            slug      = base_slug
            counter   = 1
            while Post.query.filter_by(slug=slug).first():
                slug = f'{base_slug}-{counter}'
                counter += 1

            post = Post(title=title, slug=slug, content=content,
                        excerpt=excerpt, category=category, tags=tags,
                        cover_image=cover_image, is_published=publish,
                        user_id=user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created successfully!', 'success')
            return redirect(url_for('dashboard'))

    return render_template('post_form.html', post=None, user=user, current_user=user, action='Create')


@app.route('/dashboard/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit an existing post."""
    user = get_current_user()
    post = Post.query.get_or_404(post_id)

    # Security: make sure the post belongs to this user
    if post.user_id != user.id:
        abort(403)

    if request.method == 'POST':
        post.title       = request.form.get('title', '').strip()
        post.content     = request.form.get('content', '').strip()
        post.excerpt     = request.form.get('excerpt', '').strip()
        post.category    = request.form.get('category', 'General')
        post.tags        = request.form.get('tags', '').strip()
        post.cover_image = request.form.get('cover_image', '').strip()
        post.is_published = request.form.get('publish') == 'on'
        post.updated_at  = datetime.utcnow()
        db.session.commit()
        flash('Post updated!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('post_form.html', post=post, user=user, current_user=user, action='Edit')


@app.route('/dashboard/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete a post."""
    user = get_current_user()
    post = Post.query.get_or_404(post_id)
    if post.user_id != user.id:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'info')
    return redirect(url_for('dashboard'))


# ---- PROJECTS CRUD ----

@app.route('/dashboard/projects/new', methods=['GET', 'POST'])
@login_required
def new_project():
    user = get_current_user()
    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        if not title or not description:
            flash('Title and description are required.', 'danger')
        else:
            project = Project(
                title=title, description=description,
                tech_stack   = request.form.get('tech_stack', ''),
                github_url   = request.form.get('github_url', ''),
                live_url     = request.form.get('live_url', ''),
                image_url    = request.form.get('image_url', ''),
                is_featured  = request.form.get('is_featured') == 'on',
                user_id      = user.id
            )
            db.session.add(project)
            db.session.commit()
            flash('Project added!', 'success')
            return redirect(url_for('dashboard'))
    return render_template('project_form.html', project=None, user=user, current_user=user, action='Add')


@app.route('/dashboard/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    user    = get_current_user()
    project = Project.query.get_or_404(project_id)
    if project.user_id != user.id:
        abort(403)
    if request.method == 'POST':
        project.title       = request.form.get('title', '').strip()
        project.description = request.form.get('description', '').strip()
        project.tech_stack  = request.form.get('tech_stack', '')
        project.github_url  = request.form.get('github_url', '')
        project.live_url    = request.form.get('live_url', '')
        project.image_url   = request.form.get('image_url', '')
        project.is_featured = request.form.get('is_featured') == 'on'
        db.session.commit()
        flash('Project updated!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('project_form.html', project=project, user=user, current_user=user, action='Edit')


@app.route('/dashboard/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    user    = get_current_user()
    project = Project.query.get_or_404(project_id)
    if project.user_id != user.id:
        abort(403)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted.', 'info')
    return redirect(url_for('dashboard'))


# ---- SKILLS CRUD ----

@app.route('/dashboard/skills/new', methods=['GET', 'POST'])
@login_required
def new_skill():
    user = get_current_user()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Skill name is required.', 'danger')
        else:
            skill = Skill(
                name        = name,
                category    = request.form.get('category', 'General'),
                proficiency = int(request.form.get('proficiency', 75)),
                icon        = request.form.get('icon', ''),
                user_id     = user.id
            )
            db.session.add(skill)
            db.session.commit()
            flash('Skill added!', 'success')
            return redirect(url_for('dashboard'))
    return render_template('skill_form.html', skill=None, user=user, current_user=user, action='Add')


@app.route('/dashboard/skills/<int:skill_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_skill(skill_id):
    user  = get_current_user()
    skill = Skill.query.get_or_404(skill_id)
    if skill.user_id != user.id:
        abort(403)
    if request.method == 'POST':
        skill.name        = request.form.get('name', '').strip()
        skill.category    = request.form.get('category', 'General')
        skill.proficiency = int(request.form.get('proficiency', 75))
        skill.icon        = request.form.get('icon', '')
        db.session.commit()
        flash('Skill updated!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('skill_form.html', skill=skill, user=user, current_user=user, action='Edit')


@app.route('/dashboard/skills/<int:skill_id>/delete', methods=['POST'])
@login_required
def delete_skill(skill_id):
    user  = get_current_user()
    skill = Skill.query.get_or_404(skill_id)
    if skill.user_id != user.id:
        abort(403)
    db.session.delete(skill)
    db.session.commit()
    flash('Skill removed.', 'info')
    return redirect(url_for('dashboard'))


# ---- TECHNOLOGIES CRUD ----

@app.route('/dashboard/technologies/new', methods=['GET', 'POST'])
@login_required
def new_technology():
    user = get_current_user()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Technology name is required.', 'danger')
        else:
            tech = Technology(
                name        = name,
                category    = request.form.get('category', 'Tool'),
                description = request.form.get('description', ''),
                badge_color = request.form.get('badge_color', '#0ea5e9'),
                user_id     = user.id
            )
            db.session.add(tech)
            db.session.commit()
            flash('Technology added!', 'success')
            return redirect(url_for('dashboard'))
    return render_template('tech_form.html', tech=None, user=user, current_user=user, action='Add')


@app.route('/dashboard/technologies/<int:tech_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_technology(tech_id):
    user = get_current_user()
    tech = Technology.query.get_or_404(tech_id)
    if tech.user_id != user.id:
        abort(403)
    if request.method == 'POST':
        tech.name        = request.form.get('name', '').strip()
        tech.category    = request.form.get('category', 'Tool')
        tech.description = request.form.get('description', '')
        tech.badge_color = request.form.get('badge_color', '#0ea5e9')
        db.session.commit()
        flash('Technology updated!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('tech_form.html', tech=tech, user=user, current_user=user, action='Edit')


@app.route('/dashboard/technologies/<int:tech_id>/delete', methods=['POST'])
@login_required
def delete_technology(tech_id):
    user = get_current_user()
    tech = Technology.query.get_or_404(tech_id)
    if tech.user_id != user.id:
        abort(403)
    db.session.delete(tech)
    db.session.commit()
    flash('Technology removed.', 'info')
    return redirect(url_for('dashboard'))


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(e):
    current_user = get_current_user()
    return render_template('404.html', current_user=current_user), 404


@app.errorhandler(403)
def forbidden(e):
    current_user = get_current_user()
    return render_template('403.html', current_user=current_user), 403


# ============================================================
# TEMPLATE FILTERS
# ============================================================

@app.template_filter('truncate_words')
def truncate_words(text, length=30):
    """Custom Jinja2 filter: truncate text to N words."""
    words = text.split()
    if len(words) > length:
        return ' '.join(words[:length]) + '...'
    return text


@app.template_filter('format_date')
def format_date(dt):
    """Format a datetime object nicely."""
    return dt.strftime('%B %d, %Y') if dt else ''


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == '__main__':
    # Create all database tables if they don't exist yet
    with app.app_context():
        db.create_all()
        print("✅ Database tables created!")

        # Create a sample admin user if no users exist
        if not User.query.first():
            admin = User(
                username  = 'admin',
                email     = 'admin@example.com',
                password  = generate_password_hash('admin123'),
                full_name = 'Admin User',
                bio       = 'Welcome to my blog platform! I love writing about tech and life.',
                is_admin  = True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Sample admin user created! (username: admin, password: admin123)")

    # debug=True shows helpful error messages during development
    # NEVER use debug=True in production!
    app.run(debug=True)
