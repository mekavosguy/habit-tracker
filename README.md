# 🌿 Habit Tracker Web App

A full-stack habit tracker inspired by the Notion template — with a real backend, SQLite database, and a polished frontend.

## Stack
- **Backend**: Python / Flask
- **Database**: SQLite (auto-created on first run)
- **Frontend**: Vanilla HTML/CSS/JS (served by Flask)

## Setup & Run

### Requirements
- Python 3.8+
- Flask (`pip install flask`)

### Start the app
```bash
bash start.sh
```
Then open **http://localhost:5000** in your browser.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/habits` | List all habits |
| POST | `/api/habits` | Create a habit `{name, icon, tag}` |
| DELETE | `/api/habits/:id` | Delete a habit |
| GET | `/api/checks?year=&month=` | Get checks for month |
| POST | `/api/checks/toggle` | Toggle a day `{habit_id, year, month, day}` |
| GET | `/api/stats?year=&month=` | Get stats |

---

## Features
- ✅ 12-month grid tracker — click any cell to check/uncheck
- ✅ Live stats: total checks, completion %, best habit, days logged
- ✅ Add/delete habits with icon + tag picker
- ✅ Streak counter per habit
- ✅ All data stored in SQLite (`db/habits.db`)
- ✅ Fully responsive design

## File Structure
```
habit-tracker/
├── app.py          ← Flask backend + API
├── start.sh        ← Run script
├── db/
│   └── habits.db   ← SQLite database (auto-created)
└── public/
    └── index.html  ← Frontend
```
