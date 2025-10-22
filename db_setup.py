# database/db_setup.py
import sqlite3
import os
import json


def setup_database():
    # Use consistent path with other files
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'evaluation.db')

    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("🔄 Setting up simplified database for Student API...")

    # SIMPLIFIED: Tasks received from IITM (you are the receiver)
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS received_tasks
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       timestamp
                       DATETIME
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       email
                       TEXT
                       NOT
                       NULL,
                       task
                       TEXT
                       NOT
                       NULL,
                       round
                       INTEGER
                       NOT
                       NULL,
                       nonce
                       TEXT
                       NOT
                       NULL,
                       brief
                       TEXT
                       NOT
                       NULL,
                       checks
                       TEXT,       -- Store as JSON string
                       evaluation_url
                       TEXT
                       NOT
                       NULL,
                       secret
                       TEXT
                       NOT
                       NULL,
                       status
                       TEXT
                       DEFAULT
                       'received', -- received, processing, completed, failed
                       processing_started
                       DATETIME,
                       processing_completed
                       DATETIME
                   )
                   ''')
    print("✅ received_tasks table ready")

    # SIMPLIFIED: Repositories you created
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS created_repos
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       timestamp
                       DATETIME
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       task_id
                       INTEGER
                       NOT
                       NULL,
                       repo_url
                       TEXT
                       NOT
                       NULL,
                       pages_url
                       TEXT
                       NOT
                       NULL,
                       commit_sha
                       TEXT
                       NOT
                       NULL,
                       round
                       INTEGER
                       NOT
                       NULL,
                       github_username
                       TEXT,
                       repo_name
                       TEXT,
                       FOREIGN
                       KEY
                   (
                       task_id
                   ) REFERENCES received_tasks
                   (
                       id
                   )
                       )
                   ''')
    print("✅ created_repos table ready")

    # SIMPLIFIED: Notifications you sent to IITM
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS sent_notifications
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       timestamp
                       DATETIME
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       task_id
                       INTEGER
                       NOT
                       NULL,
                       notification_url
                       TEXT
                       NOT
                       NULL,
                       success
                       BOOLEAN
                       NOT
                       NULL,
                       response_code
                       INTEGER,
                       response_message
                       TEXT,
                       attempt_number
                       INTEGER
                       DEFAULT
                       1,
                       error_details
                       TEXT,
                       FOREIGN
                       KEY
                   (
                       task_id
                   ) REFERENCES received_tasks
                   (
                       id
                   )
                       )
                   ''')
    print("✅ sent_notifications table ready")

    # SIMPLIFIED: Processing logs for debugging
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS processing_logs
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       timestamp
                       DATETIME
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       task_id
                       INTEGER
                       NOT
                       NULL,
                       log_level
                       TEXT
                       NOT
                       NULL, -- INFO, WARNING, ERROR, SUCCESS
                       message
                       TEXT
                       NOT
                       NULL,
                       details
                       TEXT,
                       FOREIGN
                       KEY
                   (
                       task_id
                   ) REFERENCES received_tasks
                   (
                       id
                   )
                       )
                   ''')
    print("✅ processing_logs table ready")

    conn.commit()
    conn.close()

    print("🎉 Database setup completed!")
    print("📊 Tables created: received_tasks, created_repos, sent_notifications, processing_logs")

    # Verify the setup
    verify_database_setup(db_path)


def verify_database_setup(db_path):
    """Verify that database was set up correctly"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check all tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        expected_tables = ['received_tasks', 'created_repos', 'sent_notifications', 'processing_logs']
        missing_tables = set(expected_tables) - set(tables)

        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False

        print("✅ All expected tables present")

        # Show table counts
        print("\n📈 Initial Database Status:")
        for table in expected_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} records")

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ Database verification failed: {e}")
        return False


def log_processing_step(task_id, log_level, message, details=None):
    """Helper function to log processing steps"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(current_dir, 'database/evaluation.db')

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
                       INSERT INTO processing_logs (task_id, log_level, message, details)
                       VALUES (?, ?, ?, ?)
                       ''', (task_id, log_level, message, details))

        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(f"❌ Failed to log processing step: {e}")


def update_task_status(task_id, status):
    """Update the status of a task"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(current_dir, 'database/evaluation.db')

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if status == 'processing':
            cursor.execute('''
                           UPDATE received_tasks
                           SET status             = ?,
                               processing_started = CURRENT_TIMESTAMP
                           WHERE id = ?
                           ''', (status, task_id))
        elif status == 'completed':
            cursor.execute('''
                           UPDATE received_tasks
                           SET status               = ?,
                               processing_completed = CURRENT_TIMESTAMP
                           WHERE id = ?
                           ''', (status, task_id))
        else:
            cursor.execute('''
                           UPDATE received_tasks
                           SET status = ?
                           WHERE id = ?
                           ''', (status, task_id))

        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(f"❌ Failed to update task status: {e}")


def get_pending_tasks():
    """Get tasks that are pending processing"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(current_dir, 'database/evaluation.db')

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT id,
                              email,
                              task,
                              round,
                              nonce,
                              brief,
                              checks,
                              evaluation_url,
                              secret
                       FROM received_tasks
                       WHERE status = 'received'
                       ORDER BY timestamp ASC
                       ''')

        tasks = cursor.fetchall()
        conn.close()
        return tasks

    except sqlite3.Error as e:
        print(f"❌ Failed to get pending tasks: {e}")
        return []


if __name__ == "__main__":
    setup_database()

    # Show usage examples
    print("\n💡 USAGE EXAMPLES:")
    print("   from db_setup import log_processing_step, update_task_status, get_pending_tasks")
    print("   log_processing_step(1, 'INFO', 'Started processing task')")
    print("   update_task_status(1, 'processing')")
    print("   pending_tasks = get_pending_tasks()")
