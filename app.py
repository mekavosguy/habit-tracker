from flask import Flask, jsonify, request, send_from_directory
import sqlite3
import os

app = Flask(__name__, static_folder='public')
DB = 'db/habits.db'

os.makedirs('db', exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            icon TEXT DEFAULT '🌟',
            tag TEXT DEFAULT 'focus',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            day INTEGER NOT NULL,
            UNIQUE(habit_id, year, month, day),
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        );
    ''')
    # Seed default habits if empty
    cur = conn.execute('SELECT COUNT(*) FROM habits')
    if cur.fetchone()[0] == 0:
        defaults = [
            ('Morning run', '🏃', 'body'),
            ('Read 30 min', '📖', 'focus'),
            ('Drink 2L water', '💧', 'health'),
            ('Meditate', '🧘', 'focus'),
            ('Eat clean', '🥗', 'health'),
        ]
        conn.executemany('INSERT INTO habits (name, icon, tag) VALUES (?,?,?)', defaults)
    conn.commit()
    conn.close()

init_db()

# --- HABITS ---

@app.route('/api/habits', methods=['GET'])
def get_habits():
    conn = get_db()
    habits = conn.execute('SELECT * FROM habits ORDER BY id').fetchall()
    conn.close()
    return jsonify([dict(h) for h in habits])

@app.route('/api/habits', methods=['POST'])
def add_habit():
    data = request.json
    name = data.get('name', '').strip()
    icon = data.get('icon', '🌟')
    tag = data.get('tag', 'focus')
    if not name:
        return jsonify({'error': 'name required'}), 400
    conn = get_db()
    cur = conn.execute('INSERT INTO habits (name, icon, tag) VALUES (?,?,?)', (name, icon, tag))
    habit_id = cur.lastrowid
    conn.commit()
    habit = conn.execute('SELECT * FROM habits WHERE id=?', (habit_id,)).fetchone()
    conn.close()
    return jsonify(dict(habit)), 201

@app.route('/api/habits/<int:habit_id>', methods=['DELETE'])
def delete_habit(habit_id):
    conn = get_db()
    conn.execute('DELETE FROM habits WHERE id=?', (habit_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# --- CHECKS ---

@app.route('/api/checks', methods=['GET'])
def get_checks():
    year = request.args.get('year', 2026, type=int)
    month = request.args.get('month', type=int)
    conn = get_db()
    if month is not None:
        rows = conn.execute(
            'SELECT habit_id, day FROM checks WHERE year=? AND month=?', (year, month)
        ).fetchall()
    else:
        rows = conn.execute(
            'SELECT habit_id, month, day FROM checks WHERE year=?', (year,)
        ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/checks/toggle', methods=['POST'])
def toggle_check():
    data = request.json
    habit_id = data['habit_id']
    year = data.get('year', 2026)
    month = data['month']
    day = data['day']
    conn = get_db()
    existing = conn.execute(
        'SELECT id FROM checks WHERE habit_id=? AND year=? AND month=? AND day=?',
        (habit_id, year, month, day)
    ).fetchone()
    if existing:
        conn.execute('DELETE FROM checks WHERE id=?', (existing['id'],))
        checked = False
    else:
        conn.execute(
            'INSERT INTO checks (habit_id, year, month, day) VALUES (?,?,?,?)',
            (habit_id, year, month, day)
        )
        checked = True
    conn.commit()
    conn.close()
    return jsonify({'checked': checked})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    year = request.args.get('year', 2026, type=int)
    month = request.args.get('month', type=int)
    conn = get_db()
    total_habits = conn.execute('SELECT COUNT(*) FROM habits').fetchone()[0]

    if month is not None:
        total_checks = conn.execute(
            'SELECT COUNT(*) FROM checks WHERE year=? AND month=?', (year, month)
        ).fetchone()[0]
        days_with_check = conn.execute(
            'SELECT COUNT(DISTINCT day) FROM checks WHERE year=? AND month=?', (year, month)
        ).fetchone()[0]
        per_habit = conn.execute(
            '''SELECT h.name, h.icon, COUNT(c.id) as count
               FROM habits h LEFT JOIN checks c ON h.id=c.habit_id AND c.year=? AND c.month=?
               GROUP BY h.id ORDER BY count DESC LIMIT 1''',
            (year, month)
        ).fetchone()
    else:
        total_checks = conn.execute(
            'SELECT COUNT(*) FROM checks WHERE year=?', (year,)
        ).fetchone()[0]
        days_with_check = 0
        per_habit = None

    conn.close()
    return jsonify({
        'total_habits': total_habits,
        'total_checks': total_checks,
        'days_with_check': days_with_check,
        'best_habit': dict(per_habit) if per_habit else None
    })

# --- SERVE FRONTEND ---
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
