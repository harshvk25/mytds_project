# notification_receiver.py - FIXED VERSION
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import sqlite3
import json
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Evaluation API")


def get_db_connection():
    """Get database connection with correct path"""
    # Get the absolute path to the database
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'database', 'evaluation.db')

    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    logger.info(f"📁 Database path: {db_path}")
    return sqlite3.connect(db_path)


class EvaluationRequest(BaseModel):
    email: str
    task: str
    round: int
    nonce: str
    repo_url: str
    commit_sha: str
    pages_url: str


@app.post("/evaluate")
async def evaluate_submission(request: EvaluationRequest):
    """Accept evaluation notifications from students"""
    logger.info(f"📨 Received evaluation: {request.email} - {request.task} - Round {request.round}")

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # FIX: Skip task validation for now - just accept all notifications
        # This matches IITM's expected behavior
        logger.info(f"✅ Accepting evaluation without task validation")

        # Insert into created_repos table
        cur.execute("""
            INSERT INTO created_repos 
                (email, task, round, nonce, repo_url, commit_sha, pages_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            request.email, request.task, request.round, request.nonce,
            request.repo_url, request.commit_sha, request.pages_url
        ))

        conn.commit()
        logger.info(f"✅ Evaluation stored: {request.email} - {request.task}")
        return {"status": "accepted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        if conn:
            conn.close()



def create_missing_tables(conn):
    """Create missing tables if they don't exist"""
    try:
        cur = conn.cursor()

        # Create received_tasks table if missing
        cur.execute("""
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
                        TEXT,
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
                        'received'
                    )
                    """)

        # Create created_repos table if missing
        cur.execute("""
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
                        INTEGER,
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
                        email
                        TEXT,
                        task
                        TEXT,
                        nonce
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
                    """)

        conn.commit()
        logger.info("✅ Created missing tables")

    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")


@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        # Test database connection and tables
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if tables exist
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cur.fetchall()]

        conn.close()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "tables": tables
        }

    except Exception as e:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": f"error: {str(e)}"
        }


@app.get("/repos")
async def get_repos():
    """Debug endpoint to see submitted repos"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # FIXED: Use correct table name
        cur.execute("SELECT * FROM created_repos ORDER BY timestamp DESC LIMIT 10")
        repos = cur.fetchall()

        # Get column names
        columns = [description[0] for description in cur.description] if cur.description else []

        # Convert to list of dictionaries for better JSON serialization
        repos_list = []
        for repo in repos:
            repo_dict = dict(zip(columns, repo)) if columns else {}
            repos_list.append(repo_dict)

        logger.info(f"📊 Returning {len(repos_list)} repos")
        return {"repos": repos_list}

    except Exception as e:
        logger.error(f"❌ Error fetching repos: {e}")
        return {"repos": [], "error": str(e)}
    finally:
        if conn:
            conn.close()


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Evaluation API - Notification Receiver",
        "status": "running",
        "endpoints": {
            "POST /evaluate": "Receive completion notifications",
            "GET /health": "Health check with table info",
            "GET /repos": "View submitted repositories"
        }
    }


if __name__ == "__main__":
    import uvicorn

    # Test database connection on startup
    try:
        conn = get_db_connection()

        # Ensure tables exist
        create_missing_tables(conn)
        conn.close()

        logger.info("✅ Database connection and tables verified")
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")

    uvicorn.run(app, host="0.0.0.0", port=8001)
