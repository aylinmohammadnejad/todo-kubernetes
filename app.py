from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key for security

# Database path
DATABASE = 'todo.db'

# Database connection
def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

# Initialize database if needed
def init_db():
    if not os.path.exists(DATABASE):
        with get_db() as db:
            db.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            ''')
            db.execute('''
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            db.commit()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    with get_db() as db:
        tasks = db.execute(
            'SELECT id, title FROM tasks WHERE user_id = ?',
            (session['user_id'],)
        ).fetchall()
    
    return render_template('index.html', tasks=tasks)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            with get_db() as db:
                db.execute(
                    'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                    (username, generate_password_hash(password))
                )
                db.commit()
            
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with get_db() as db:
            user = db.execute(
                'SELECT * FROM users WHERE username = ?',
                (username,)
            ).fetchone()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!')
            return redirect(url_for('index'))
        
        flash('Invalid username or password.')
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
def add():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    title = request.form['title']
    with get_db() as db:
        db.execute(
            'INSERT INTO tasks (user_id, title) VALUES (?, ?)',
            (session['user_id'], title)
        )
        db.commit()
    
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    with get_db() as db:
        db.execute(
            'DELETE FROM tasks WHERE id = ? AND user_id = ?',
            (id, session['user_id'])
        )
        db.commit()
    
    return redirect(url_for('index'))

# ----------- API ROUTES -----------

@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    with get_db() as db:
        tasks = db.execute(
            'SELECT id, title FROM tasks WHERE user_id = ?',
            (session['user_id'],)
        ).fetchall()
    
    return jsonify([{'id': task['id'], 'title': task['title']} for task in tasks])

@app.route('/api/tasks', methods=['POST'])
def api_add_task():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    title = data.get('title', '').strip()
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    with get_db() as db:
        cursor = db.execute(
            'INSERT INTO tasks (user_id, title) VALUES (?, ?)',
            (session['user_id'], title)
        )
        db.commit()
        task_id = cursor.lastrowid
    
    return jsonify({'id': task_id, 'title': title}), 201

@app.route('/api/tasks/<int:id>', methods=['GET'])
def api_get_task(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    with get_db() as db:
        task = db.execute(
            'SELECT id, title FROM tasks WHERE id = ? AND user_id = ?',
            (id, session['user_id'])
        ).fetchone()
    
    if task:
        return jsonify({'id': task['id'], 'title': task['title']})
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def api_delete_task(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    with get_db() as db:
        result = db.execute(
            'DELETE FROM tasks WHERE id = ? AND user_id = ?',
            (id, session['user_id'])
        )
        db.commit()
    
    if result.rowcount:
        return jsonify({'message': 'Task deleted'})
    return jsonify({'error': 'Task not found'}), 404

# -----------

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)