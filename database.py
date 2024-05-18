import sqlite3


def init_db():
    conn = sqlite3.connect('work_hours.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS work_hours (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            hours INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
