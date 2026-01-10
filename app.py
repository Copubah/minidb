"""Demo web app using MiniDB - A simple task manager."""

from flask import Flask, render_template, request, redirect, url_for, flash
from minidb.engine import Database
from minidb.executor import Executor

app = Flask(__name__)
app.secret_key = 'minidb-demo-secret'

# Initialize database
db = Database('tasks.json')
executor = Executor(db)

# Create tasks table if not exists
if 'tasks' not in db.tables:
    executor.execute('''
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT,
            priority INTEGER
        )
    ''')

def get_next_id():
    """Get next available ID."""
    result = executor.execute('SELECT id FROM tasks ORDER BY id DESC LIMIT 1')
    if result.rows:
        return result.rows[0]['id'] + 1
    return 1

@app.route('/')
def index():
    """List all tasks."""
    result = executor.execute('SELECT * FROM tasks ORDER BY priority DESC')
    return render_template('index.html', tasks=result.rows)

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    """Add a new task."""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        priority = request.form.get('priority', 1)
        
        task_id = get_next_id()
        sql = f"INSERT INTO tasks (id, title, description, status, priority) VALUES ({task_id}, '{title}', '{description}', 'pending', {priority})"
        
        try:
            executor.execute(sql)
            flash('Task added successfully!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'error')
        
        return redirect(url_for('index'))
    
    return render_template('add.html')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    """Edit a task."""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        status = request.form.get('status', 'pending')
        priority = request.form.get('priority', 1)
        
        sql = f"UPDATE tasks SET title = '{title}', description = '{description}', status = '{status}', priority = {priority} WHERE id = {task_id}"
        
        try:
            executor.execute(sql)
            flash('Task updated successfully!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'error')
        
        return redirect(url_for('index'))
    
    result = executor.execute(f'SELECT * FROM tasks WHERE id = {task_id}')
    if not result.rows:
        flash('Task not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('edit.html', task=result.rows[0])

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    """Delete a task."""
    try:
        executor.execute(f'DELETE FROM tasks WHERE id = {task_id}')
        flash('Task deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    
    return redirect(url_for('index'))

@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    """Mark task as complete."""
    try:
        executor.execute(f"UPDATE tasks SET status = 'completed' WHERE id = {task_id}")
        flash('Task marked as complete!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    
    return redirect(url_for('index'))

@app.route('/sql', methods=['GET', 'POST'])
def sql_console():
    """SQL console for direct queries."""
    result = None
    error = None
    sql = ''
    
    if request.method == 'POST':
        sql = request.form.get('sql', '')
        try:
            result = executor.execute(sql)
        except Exception as e:
            error = str(e)
    
    return render_template('sql.html', sql=sql, result=result, error=error)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
