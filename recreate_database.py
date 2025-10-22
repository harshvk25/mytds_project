# recreate_database.py
import sqlite3
import os


def recreate_database():
    # Use consistent path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'database/evaluation.db')

    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Remove existing database file if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️  Removed old database file")

    # Create new database with SIMPLIFIED tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("📊 Creating simplified database tables...")

    # SIMPLIFIED: Only track tasks YOU receive from IITM
    cursor.execute('''
                   CREATE TABLE received_tasks
                   (
                       id             INTEGER PRIMARY KEY AUTOINCREMENT,
                       timestamp      DATETIME DEFAULT CURRENT_TIMESTAMP,
                       email          TEXT,
                       task           TEXT,
                       round          INTEGER,
                       nonce          TEXT,
                       brief          TEXT,
                       checks         TEXT,
                       evaluation_url TEXT,
                       secret         TEXT,
                       status         TEXT     DEFAULT 'pending'
                   )
                   ''')
    print("✅ Created received_tasks table")

    # SIMPLIFIED: Only track repositories YOU create
    cursor.execute('''
                   CREATE TABLE created_repos
                   (
                       id         INTEGER PRIMARY KEY AUTOINCREMENT,
                       timestamp  DATETIME DEFAULT CURRENT_TIMESTAMP,
                       task_id    INTEGER,
                       repo_url   TEXT,
                       pages_url  TEXT,
                       commit_sha TEXT,
                       round      INTEGER,
                       FOREIGN KEY (task_id) REFERENCES received_tasks (id)
                   )
                   ''')
    print("✅ Created created_repos table")

    # SIMPLIFIED: Only track notifications YOU send to IITM
    cursor.execute('''
                   CREATE TABLE sent_notifications
                   (
                       id            INTEGER PRIMARY KEY AUTOINCREMENT,
                       timestamp     DATETIME DEFAULT CURRENT_TIMESTAMP,
                       task_id       INTEGER,
                       success       BOOLEAN,
                       response_code INTEGER,
                       error_message TEXT,
                       FOREIGN KEY (task_id) REFERENCES received_tasks (id)
                   )
                   ''')
    print("✅ Created sent_notifications table")

    conn.commit()
    conn.close()
    print("🎉 Database recreated with simplified tables!")

    # Verify tables were created
    verify_tables(db_path)


def verify_tables(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print("\n📋 TABLES IN DATABASE:")
    for table in tables:
        # Show table structure
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print(f"  - {table[0]}: {len(columns)} columns")
        for col in columns:
            print(f"      {col[1]} ({col[2]})")

    conn.close()


def check_database_status():
    """Quick check of database status"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'database/evaluation.db')

    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("\n📈 DATABASE STATUS:")

        # Count records in each table
        tables = ['received_tasks', 'created_repos', 'sent_notifications']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} records")

        # Show recent tasks
        cursor.execute("""
                       SELECT task, round, status, datetime(timestamp)
                       FROM received_tasks
                       ORDER BY timestamp DESC
                           LIMIT 3
                       """)
        recent_tasks = cursor.fetchall()

        if recent_tasks:
            print(f"\n🕒 RECENT TASKS:")
            for task in recent_tasks:
                print(f"  - {task[0]} (Round {task[1]}) - {task[2]} - {task[3]}")

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "status":
        check_database_status()
    else:
        recreate_database()
        print("\n💡 Usage: python recreate_database.py [status]")
        print("   - No arguments: Recreate database")
        print("   - 'status': Check current database status")
