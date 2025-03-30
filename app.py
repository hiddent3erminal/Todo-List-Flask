import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)
DATABASE = 'database.db'

# Ensure the database exists
def init_db():
    if not os.path.exists(DATABASE):
        print("Database file not found. Creating a new one...")
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT 0
                )
            ''')
            conn.commit()
            print("Database initialized.")

# Get database connection
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id, name, done FROM tasks')
        tasks = [{'id': row[0], 'name': row[1], 'done': bool(row[2])} for row in cursor.fetchall()]
        return render_template('index.html', tasks=tasks)
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return "An error occurred while fetching tasks."

@app.route('/add', methods=['POST'])
def add_task():
    task_name = request.form.get('task')
    if task_name:
        try:
            db = get_db()
            db.execute('INSERT INTO tasks (name) VALUES (?)', (task_name,))
            db.commit()
        except Exception as e:
            print(f"Error adding task: {e}")
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    try:
        db = get_db()
        db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        db.commit()
    except Exception as e:
        print(f"Error deleting task: {e}")
    return redirect(url_for('index'))

@app.route('/done/<int:task_id>', methods=['POST'])
def mark_done(task_id):
    try:
        db = get_db()
        db.execute('UPDATE tasks SET done = 1 WHERE id = ?', (task_id,))
        db.commit()
    except Exception as e:
        print(f"Error marking task as done: {e}")
    return redirect(url_for('index'))

@app.route('/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    updated_task = request.form.get('updated_task')
    if updated_task:
        try:
            db = get_db()
            db.execute('UPDATE tasks SET name = ? WHERE id = ?', (updated_task, task_id))
            db.commit()
        except Exception as e:
            print(f"Error updating task: {e}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()  # Ensure the database is initialized before starting the app
    app.run(debug=True)
