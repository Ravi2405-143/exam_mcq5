import sqlite3
import random

DB_PATH = "exam.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_questions(limit, subject=None, exclude_ids=None):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        exclude_sql = ""
        params = []
        
        if exclude_ids:
            placeholders = ','.join('?' for _ in exclude_ids)
            exclude_sql = f" AND id NOT IN ({placeholders})"
            params.extend(exclude_ids)

        if subject and subject != "Combined":
            query = f"SELECT * FROM questions WHERE subject = ?{exclude_sql} ORDER BY RANDOM() LIMIT ?"
            params.insert(0, subject)
            params.append(limit)
            print(f"Executing: {query} with {params[:2]}... (total params: {len(params)})")
            cur.execute(query, params)
        else:
            query = f"SELECT * FROM questions WHERE 1=1{exclude_sql} ORDER BY RANDOM() LIMIT ?"
            params.append(limit)
            cur.execute(query, params)
            
        rows = cur.fetchall()
        print(f"Initial fetch got {len(rows)} questions")
        
        if len(rows) < limit and exclude_ids:
            print("Fallback triggered")
            if subject and subject != "Combined":
                cur.execute("SELECT * FROM questions WHERE subject = ? ORDER BY RANDOM() LIMIT ?", (subject, limit))
            else:
                cur.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT ?", (limit,))
            rows = cur.fetchall()
            print(f"Fallback fetch got {len(rows)} questions")
            
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

# Test with one of the subjects
subjects_to_test = [
    "G&SR Basics & Signals",
    "Block Working Manual (BWM)",
    "Operating Manual (OM)"
]

for sub in subjects_to_test:
    print(f"\n--- Testing subject: {sub} ---")
    res = get_questions(10, sub)
    if not res:
        print(f"FAILED: No questions found for {sub}")
    else:
        print(f"SUCCESS: Found {len(res)} questions")

# Test with exclude_ids that shouldn't exclude everything
print("\n--- Testing with exclude_ids ---")
res = get_questions(10, "G&SR Basics & Signals", exclude_ids=[1, 2, 3])
if not res:
    print("FAILED: No questions found with exclude_ids")
else:
    print(f"SUCCESS: Found {len(res)} questions")
