import sqlite3

SUBJECTS = [
    "G&SR Basics & Signals",
    "Block Working Manual (BWM)",
    "Accident Manual & Disaster Mgmt",
    "Operating Manual (OM)",
    "Establishment & Financial Rules",
    "Engineering & P-Way Rules",
    "S&T (Signals & Telecomm) Rules",
    "Carriage & Wagon (C&W) Rules",
    "Loco Rules & Operation",
    "Store Rules & Procedures"
]

try:
    conn = sqlite3.connect('exam.db')
    cur = conn.cursor()
    
    print("--- Database Subject Summary ---")
    cur.execute("SELECT subject, COUNT(*) FROM questions GROUP BY subject")
    db_counts = dict(cur.fetchall())
    
    total_in_db = 0
    for s in SUBJECTS:
        count = db_counts.get(s, 0)
        print(f"'{s}': {count} questions")
        total_in_db += count
        
    print(f"\nTotal questions under known subjects: {total_in_db}")
    
    other_subjects = {k: v for k, v in db_counts.items() if k not in SUBJECTS}
    if other_subjects:
        print("\nOther subjects found in database:")
        for k, v in other_subjects.items():
            print(f"'{k}': {v} questions")
    else:
        print("\nNo other subjects found.")
        
    cur.execute("SELECT COUNT(*) FROM questions WHERE subject IS NULL")
    null_count = cur.fetchone()[0]
    print(f"Questions with NULL subject: {null_count}")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
