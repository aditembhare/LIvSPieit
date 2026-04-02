from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import date, datetime
from functools import wraps
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'living_spiritz_secret_2024'

# ─── Database Configuration ────────────────────────────────────────────────
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',          # XAMPP default — update if needed
    'database': 'living_spiritz'
}

def get_db():
    """Try to connect to MySQL. If fails, return MockConn for graceful degradation."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Exception as e:
        print(f"[DB] Could not connect: {e} — running in MOCK MODE.")
    return MockConn()

# ─── Mock Database (fallback when MySQL is unavailable) ────────────────────
class MockCursor:
    def __init__(self, dictionary=False):
        self.dictionary = dictionary
        self.lastrowid = 1
    def execute(self, query, params=None): pass
    def executemany(self, query, params_list): pass
    def fetchone(self):
        if self.dictionary:
            return {'c': 0, 'cnt': 0, 'avg': 0, 'username': 'Guest',
                    'email': 'guest@example.com', 'id': 1, 's': 3,
                    'theme': 'light', 'notifications': 1, 'timezone': 'Asia/Kolkata'}
        return (0,)
    def fetchall(self): return []
    def close(self): pass

class MockConn:
    def cursor(self, dictionary=False): return MockCursor(dictionary)
    def commit(self): pass
    def close(self): pass
    def is_connected(self): return False

# ─── Auth Decorator ────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ─── Jinja2 Global Helpers ─────────────────────────────────────────────────
@app.context_processor
def inject_globals():
    today = date.today()
    uid = session.get('user_id', 1)
    score = compute_wellness_score(uid)[0] if 'user_id' in session else 84
    return {
        'now_date': today.strftime('%B %d, %Y'),
        'now_str': today.strftime('%Y-%m-%d'),
        'wellness_score': score,
        'current_user': session.get('username', None),
        'is_logged_in': 'user_id' in session,
    }

# ─── Wellness Score Calculator ─────────────────────────────────────────────
def compute_wellness_score(user_id=1):
    conn = get_db()
    if isinstance(conn, MockConn):
        return 84, 2, 3, 1
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT COUNT(*) AS c FROM habits WHERE user_id=%s AND last_completed=%s",
                (user_id, date.today()))
    done_today = cur.fetchone()['c']

    cur.execute("SELECT COUNT(*) AS c FROM habits WHERE user_id=%s", (user_id,))
    total_habits = max(cur.fetchone()['c'], 1)

    cur.execute("SELECT COUNT(*) AS c FROM mood_logs WHERE user_id=%s AND created_at >= NOW() - INTERVAL 7 DAY", (user_id,))
    mood_entries = cur.fetchone()['c']

    cur.execute("SELECT COUNT(*) AS c FROM reflections WHERE user_id=%s AND created_at >= NOW() - INTERVAL 7 DAY", (user_id,))
    refl_entries = cur.fetchone()['c']

    cur.execute("SELECT COALESCE(AVG(current_value/NULLIF(target_value,0)*100),0) AS avg FROM goals WHERE user_id=%s", (user_id,))
    goal_avg = float(cur.fetchone()['avg'] or 0)

    cur.close()
    conn.close()

    score = min(
        int((done_today / total_habits) * 40)
        + min(mood_entries * 5, 20)
        + min(refl_entries * 5, 20)
        + int(goal_avg / 5)
        + 10, 100
    )
    return score, done_today, total_habits, mood_entries

# ─── Database Initialisation ───────────────────────────────────────────────
def init_db():
    conn = get_db()
    if isinstance(conn, MockConn):
        print("[INFO] Mock Mode — skipping DB init.")
        return
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        theme VARCHAR(20) DEFAULT 'light',
        notifications TINYINT DEFAULT 1,
        timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS habits (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        name VARCHAR(100),
        description VARCHAR(255),
        icon VARCHAR(50) DEFAULT 'checklist',
        streak INT DEFAULT 0,
        last_completed DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS mood_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        mood_level VARCHAR(20),
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS reflections (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        title VARCHAR(255),
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS goals (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        title VARCHAR(255),
        category VARCHAR(100),
        target_value INT DEFAULT 100,
        current_value INT DEFAULT 0,
        unit VARCHAR(50),
        deadline DATE,
        priority TINYINT DEFAULT 2,
        status VARCHAR(20) DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )""")
    try:
        cur.execute("ALTER TABLE goals ADD COLUMN priority TINYINT DEFAULT 2")
        cur.execute("ALTER TABLE goals ADD COLUMN status VARCHAR(20) DEFAULT 'active'")
    except Error:
        pass
        
    cur.execute("""CREATE TABLE IF NOT EXISTS goal_updates (
        id INT AUTO_INCREMENT PRIMARY KEY,
        goal_id INT NOT NULL,
        update_value INT DEFAULT 0,
        note VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
    )""")

    conn.commit()
    cur.close()
    conn.close()

# ═══════════════════════════════════════════════════════════════════════════
# AUTH ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html', current_page='register')

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html', current_page='register')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html', current_page='register')

        conn = get_db()
        if isinstance(conn, MockConn):
            flash('Database not available. Please configure MySQL.', 'error')
            return render_template('register.html', current_page='register')

        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            flash('An account with that email already exists.', 'error')
            cur.close(); conn.close()
            return render_template('register.html', current_page='register')

        hashed = generate_password_hash(password)
        cur.execute(
            "INSERT INTO users (username, email, password) VALUES (%s,%s,%s)",
            (username, email, hashed)
        )
        conn.commit()
        uid = cur.lastrowid

        # Seed starter habits
        cur.executemany(
            "INSERT INTO habits (user_id, name, description, icon, streak) VALUES (%s,%s,%s,%s,%s)",
            [
                (uid, 'Morning Meditation', '10 minutes of mindfulness', 'self_improvement', 0),
                (uid, 'Evening Reading',    'Read 20 pages before bed', 'auto_stories', 0),
                (uid, 'Hydration',          'Drink 2.5L of water',       'water_drop', 0),
            ]
        )
        conn.commit()
        cur.close(); conn.close()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', current_page='register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        conn = get_db()
        if isinstance(conn, MockConn):
            flash('Database not available. Please configure MySQL.', 'error')
            return render_template('login.html', current_page='login')

        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close(); conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id']  = user['id']
            session['username'] = user['username']
            session['email']    = user['email']
            session['theme']    = user.get('theme', 'light')
            flash(f"Welcome back, {user['username']}!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html', current_page='login')


@app.route('/logout')
def logout():
    name = session.get('username', 'User')
    session.clear()
    flash(f"Goodbye, {name}! See you soon.", 'success')
    return redirect(url_for('home'))


# ═══════════════════════════════════════════════════════════════════════════
# SETTINGS ROUTE
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    uid = session['user_id']

    if request.method == 'POST':
        action = request.form.get('action')

        conn = get_db()
        if isinstance(conn, MockConn):
            flash('Database not available.', 'error')
            return redirect(url_for('settings'))

        cur = conn.cursor(dictionary=True)

        if action == 'profile':
            username = request.form.get('username', '').strip()
            email    = request.form.get('email', '').strip().lower()
            timezone = request.form.get('timezone', 'Asia/Kolkata')

            if not username or not email:
                flash('Username and email are required.', 'error')
            else:
                # Check email uniqueness
                cur.execute("SELECT id FROM users WHERE email=%s AND id!=%s", (email, uid))
                if cur.fetchone():
                    flash('That email is already used by another account.', 'error')
                else:
                    cur.execute(
                        "UPDATE users SET username=%s, email=%s, timezone=%s WHERE id=%s",
                        (username, email, timezone, uid)
                    )
                    conn.commit()
                    session['username'] = username
                    session['email']    = email
                    flash('Profile updated successfully!', 'success')

        elif action == 'password':
            current_pw = request.form.get('current_password', '')
            new_pw     = request.form.get('new_password', '')
            confirm_pw = request.form.get('confirm_password', '')

            cur.execute("SELECT password FROM users WHERE id=%s", (uid,))
            row = cur.fetchone()

            if not row or not check_password_hash(row['password'], current_pw):
                flash('Current password is incorrect.', 'error')
            elif new_pw != confirm_pw:
                flash('New passwords do not match.', 'error')
            elif len(new_pw) < 6:
                flash('Password must be at least 6 characters.', 'error')
            else:
                cur.execute("UPDATE users SET password=%s WHERE id=%s",
                            (generate_password_hash(new_pw), uid))
                conn.commit()
                flash('Password changed successfully!', 'success')

        elif action == 'preferences':
            theme         = request.form.get('theme', 'light')
            notifications = 1 if request.form.get('notifications') else 0
            cur.execute("UPDATE users SET theme=%s, notifications=%s WHERE id=%s",
                        (theme, notifications, uid))
            conn.commit()
            session['theme'] = theme
            flash('Preferences saved!', 'success')

        elif action == 'delete_account':
            confirm = request.form.get('confirm_delete', '')
            if confirm == session.get('username'):
                cur.execute("DELETE FROM users WHERE id=%s", (uid,))
                conn.commit()
                session.clear()
                flash('Your account has been deleted.', 'success')
                cur.close(); conn.close()
                return redirect(url_for('home'))
            else:
                flash('Username did not match. Account not deleted.', 'error')

        cur.close(); conn.close()
        return redirect(url_for('settings'))

    # GET — load user data
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE id=%s", (uid,))
    user = cur.fetchone() or {
        'username': session.get('username', ''),
        'email':    session.get('email', ''),
        'theme': 'light', 'notifications': 1, 'timezone': 'Asia/Kolkata'
    }
    cur.close(); conn.close()
    return render_template('settings.html', current_page='settings', user=user)


# ═══════════════════════════════════════════════════════════════════════════
# APP ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/')
def home():
    return render_template('home.html', current_page='home')


@app.route('/dashboard')
@login_required
def dashboard():
    uid = session['user_id']
    score, done_today, total_habits, mood_cnt = compute_wellness_score(uid)

    conn = get_db()
    habits, latest_mood, latest_reflection = [], None, None
    user = {'username': session.get('username', 'User')}

    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM habits WHERE user_id=%s LIMIT 6", (uid,))
    habits = cur.fetchall()
    cur.execute("SELECT mood_level, created_at FROM mood_logs WHERE user_id=%s ORDER BY created_at DESC LIMIT 1", (uid,))
    latest_mood = cur.fetchone()
    cur.execute("SELECT title, created_at FROM reflections WHERE user_id=%s ORDER BY created_at DESC LIMIT 1", (uid,))
    latest_reflection = cur.fetchone()
    cur.close(); conn.close()

    return render_template('dashboard.html',
        current_page='dashboard',
        habits=habits,
        latest_mood=latest_mood,
        latest_reflection=latest_reflection,
        wellness_score=score,
        habits_today=done_today,
        total_habits=total_habits,
        user=user,
    )


@app.route('/habits')
@login_required
def habits():
    uid = session['user_id']
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM habits WHERE user_id=%s ORDER BY streak DESC", (uid,))
    habits_list = cur.fetchall()
    cur.close(); conn.close()
    
    # Calculate activity map (last 28 days) based on streaks
    from datetime import timedelta
    today = date.today()
    activity_map = [0] * 28
    for h in habits_list:
        if h['last_completed'] and h['streak'] > 0:
            end_date = h['last_completed']
            start_date = end_date - timedelta(days=h['streak'] - 1)
            for i in range(28):
                d = today - timedelta(days=27 - i)
                if start_date <= d <= end_date:
                    activity_map[i] += 1
                    
    max_habits = len(habits_list) or 1
    opacities = []
    for count in activity_map:
        opacity = max(20, int((count / max_habits) * 100)) if count > 0 else 0
        opacities.append(opacity)
        
    return render_template('habits.html', current_page='habits', habits=habits_list, today=today, opacities=opacities)


@app.route('/habits/check/<int:habit_id>', methods=['POST'])
@login_required
def check_habit(habit_id):
    uid = session['user_id']
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM habits WHERE id=%s AND user_id=%s", (habit_id, uid))
    h = cur.fetchone()
    if h:
        today = date.today()
        if h['last_completed'] != today:
            cur.execute("UPDATE habits SET streak=%s, last_completed=%s WHERE id=%s",
                        ((h['streak'] or 0) + 1, today, habit_id))
            conn.commit()
    cur.close(); conn.close()
    return redirect(url_for('habits'))


@app.route('/habits/add', methods=['POST'])
@login_required
def add_habit():
    uid  = session['user_id']
    name = request.form.get('name', '').strip()
    desc = request.form.get('description', '').strip()
    icon = request.form.get('icon', 'checklist')
    if name:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO habits (user_id, name, description, icon) VALUES (%s,%s,%s,%s)",
                    (uid, name, desc, icon))
        conn.commit()
        cur.close(); conn.close()
        flash('Habit created!', 'success')
    return redirect(url_for('habits'))


@app.route('/habits/delete/<int:habit_id>', methods=['POST'])
@login_required
def delete_habit(habit_id):
    uid = session['user_id']
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM habits WHERE id=%s AND user_id=%s", (habit_id, uid))
    conn.commit()
    cur.close(); conn.close()
    flash('Habit deleted.', 'success')
    return redirect(url_for('habits'))


@app.route('/mood', methods=['GET', 'POST'])
@login_required
def mood():
    uid = session['user_id']
    if request.method == 'POST':
        mood_level = request.form.get('mood_level', 'neutral')
        note       = request.form.get('note', '')
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO mood_logs (user_id, mood_level, note) VALUES (%s,%s,%s)",
                    (uid, mood_level, note))
        conn.commit()
        cur.close(); conn.close()
        flash('Mood logged!', 'success')
        return redirect(url_for('mood'))

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM mood_logs WHERE user_id=%s ORDER BY created_at DESC LIMIT 10", (uid,))
    timeline = cur.fetchall()
    cur.execute("""
        SELECT DAYOFWEEK(created_at) AS dow, COUNT(*) AS cnt, mood_level
        FROM mood_logs WHERE user_id=%s AND created_at >= NOW() - INTERVAL 7 DAY
        GROUP BY dow, mood_level ORDER BY dow
    """, (uid,))
    weekly = cur.fetchall()
    cur.close(); conn.close()
    return render_template('mood.html', current_page='mood', mood_timeline=timeline, weekly_data=weekly)


@app.route('/reflection', methods=['GET', 'POST'])
@login_required
def reflection():
    uid = session['user_id']
    if request.method == 'POST':
        title   = request.form.get('title', '').strip() or 'Untitled'
        content = request.form.get('content', '').strip()
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO reflections (user_id, title, content) VALUES (%s,%s,%s)",
                    (uid, title, content))
        conn.commit()
        cur.close(); conn.close()
        flash('Reflection saved!', 'success')
        return redirect(url_for('reflection'))

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM reflections WHERE user_id=%s ORDER BY created_at DESC LIMIT 20", (uid,))
    entries = cur.fetchall()
    cur.execute("SELECT COUNT(DISTINCT DATE(created_at)) AS s FROM reflections WHERE user_id=%s AND created_at >= NOW() - INTERVAL 14 DAY", (uid,))
    row = cur.fetchone()
    streak = row['s'] if row else 0
    cur.close(); conn.close()
    return render_template('reflection.html', current_page='reflection', reflections=entries, streak=streak)


@app.route('/tools')
@login_required
def tools():
    return render_template('tools.html', current_page='tools')


@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    uid = session['user_id']
    if request.method == 'POST':
        title  = request.form.get('title', '').strip()
        cat    = request.form.get('category', 'Personal')
        target = int(request.form.get('target_value', 100))
        unit   = request.form.get('unit', '')
        dl     = request.form.get('deadline') or None
        priority = int(request.form.get('priority', 2))
        if title:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO goals (user_id, title, category, target_value, unit, deadline, priority, status) VALUES (%s,%s,%s,%s,%s,%s,%s,'active')",
                        (uid, title, cat, target, unit, dl, priority))
            conn.commit()
            cur.close(); conn.close()
        return redirect(url_for('goals'))

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM goals WHERE user_id=%s ORDER BY priority DESC, created_at DESC", (uid,))
    goals_list = cur.fetchall()
    
    from datetime import date, datetime
    today = date.today()
    for g in goals_list:
        g['percent'] = min(int((g['current_value'] / max(g['target_value'], 1)) * 100), 100)
        if g['deadline']:
            if isinstance(g['deadline'], date):
                delta = (g['deadline'] - today).days
            else:
                d = datetime.strptime(str(g['deadline']), "%Y-%m-%d").date()
                delta = (d - today).days
            g['days_remaining'] = delta if delta > 0 else 0
        else:
            g['days_remaining'] = None

    active   = [g for g in goals_list if g.get('status', 'active') == 'active' and g['percent'] < 100]
    daily_focus = [g for g in active if g.get('priority', 2) == 3]
    achieved = [g for g in goals_list if g['percent'] >= 100 or g.get('status') == 'completed']
    
    avg      = sum(g['percent'] for g in goals_list) / max(len(goals_list), 1)
    stats = {'total': len(goals_list), 'active': len(active), 'daily_focus': len(daily_focus), 'achieved': len(achieved), 'avg_completion': int(avg)}
    cur.close(); conn.close()
    return render_template('goals.html', current_page='goals', goals=goals_list, daily_focus=daily_focus, active_goals=active, achieved_goals=achieved, stats=stats)


@app.route('/goals/update/<int:goal_id>', methods=['POST'])
@login_required
def update_goal(goal_id):
    uid = session['user_id']
    action = request.form.get('action', 'update')
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("SELECT current_value, target_value FROM goals WHERE id=%s AND user_id=%s", (goal_id, uid))
    goal = cur.fetchone()
    if goal:
        if action == 'increment':
            inc_val = int(request.form.get('increment_value', 1))
            new_val = min(goal['current_value'] + inc_val, goal['target_value'])
        elif action == 'set':
            new_val = int(request.form.get('current_value', goal['current_value']))
            new_val = min(max(new_val, 0), goal['target_value'])
        else:
            new_val = int(request.form.get('current_value', goal['current_value']))
            new_val = min(max(new_val, 0), goal['target_value'])
            
        status = 'completed' if new_val >= goal['target_value'] else 'active'
        diff = new_val - goal['current_value']
        
        cur.execute("UPDATE goals SET current_value=%s, status=%s WHERE id=%s AND user_id=%s", (new_val, status, goal_id, uid))
        if diff != 0:
            cur.execute("INSERT INTO goal_updates (goal_id, update_value) VALUES (%s, %s)", (goal_id, diff))
        conn.commit()
    cur.close(); conn.close()
    return redirect(url_for('goals'))


@app.route('/insights')
@login_required
def insights():
    uid = session['user_id']
    score, _, _, _ = compute_wellness_score(uid)
    data = {'top_habits': [], 'mood_dist': [], 'reflections_month': 0, 'goals': []}
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT name, streak FROM habits WHERE user_id=%s ORDER BY streak DESC LIMIT 5", (uid,))
    data['top_habits'] = cur.fetchall()
    cur.execute("SELECT mood_level, COUNT(*) AS cnt FROM mood_logs WHERE user_id=%s GROUP BY mood_level ORDER BY cnt DESC", (uid,))
    data['mood_dist'] = cur.fetchall()
    cur.execute("SELECT COUNT(*) AS c FROM reflections WHERE user_id=%s AND created_at >= NOW() - INTERVAL 30 DAY", (uid,))
    row = cur.fetchone()
    data['reflections_month'] = row['c'] if row else 0
    cur.execute("SELECT title, current_value, target_value FROM goals WHERE user_id=%s", (uid,))
    raw = cur.fetchall()
    data['goals'] = [{'title': g['title'], 'percent': min(int((g['current_value'] / max(g['target_value'], 1)) * 100), 100)} for g in raw]
    
    # Weekly Activity Chart Data
    from datetime import timedelta
    today = date.today()
    weekly_activity = [0] * 7
    days_names = [(today - timedelta(days=6-i)).strftime('%a') for i in range(7)]
    days_names[6] = 'Today'
    data['weekly_days'] = days_names
    
    cur.execute("SELECT last_completed, streak FROM habits WHERE user_id=%s", (uid,))
    all_habits = cur.fetchall()
    for h in all_habits:
        if h['last_completed'] and h['streak'] > 0:
            end_date = h['last_completed']
            start_date = end_date - timedelta(days=h['streak'] - 1)
            for i in range(7):
                d = today - timedelta(days=6 - i)
                if start_date <= d <= end_date:
                    weekly_activity[i] += 1
                    
    cur.execute("SELECT DATE(created_at) as d, COUNT(*) as c FROM mood_logs WHERE user_id=%s AND created_at >= NOW() - INTERVAL 7 DAY GROUP BY DATE(created_at)", (uid,))
    for row in cur.fetchall():
        d = row['d']
        delta = (today - d).days
        if 0 <= delta <= 6:
            weekly_activity[6 - delta] += row['c'] * 2
            
    cur.execute("SELECT DATE(created_at) as d, COUNT(*) as c FROM reflections WHERE user_id=%s AND created_at >= NOW() - INTERVAL 7 DAY GROUP BY DATE(created_at)", (uid,))
    for row in cur.fetchall():
        d = row['d']
        delta = (today - d).days
        if 0 <= delta <= 6:
            weekly_activity[6 - delta] += row['c'] * 3
            
    max_act = max(weekly_activity) if max(weekly_activity) > 0 else 1
    data['weekly_heights'] = [max(10, int((a / max_act) * 100)) for a in weekly_activity]
    cur.close(); conn.close()
    return render_template('insights.html', current_page='insights', data=data, wellness_score=score)


@app.route('/community')
def community():
    return render_template('community.html', current_page='community')


# ─── Entry Point ─────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
