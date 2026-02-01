import sqlite3

DB_PATH = "exam.db"

# Ranges provided by the user
CATEGORIES = [
    ("G&SR Basics & Signals", 1, 800),
    ("Block Working Manual (BWM)", 801, 1200),
    ("Accident Manual & Disaster Mgmt", 1201, 1550),
    ("Operating Manual (OM)", 1551, 1950),
    ("Establishment & Financial Rules", 1951, 2250),
    ("Engineering & P-Way Rules", 2251, 2550),
    ("S&T (Signals & Telecomm) Rules", 2551, 2800),
    ("Carriage & Wagon (C&W) Rules", 2801, 3000),
    ("Loco Rules & Operation", 3001, 3200),
    ("Store Rules & Procedures", 3201, 3500)
]

def rebuild_categories():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        print("Starting re-categorization...")
        
        total_updated = 0
        for subject, start, end in CATEGORIES:
            cur.execute(
                "UPDATE questions SET subject = ? WHERE question_no BETWEEN ? AND ?",
                (subject, start, end)
            )
            updated = cur.rowcount
            print(f"Updated '{subject}': {updated} questions (Range: {start}-{end})")
            total_updated += updated
            
        conn.commit()
        print(f"\nTotal questions updated: {total_updated}")
        
        # Check if any questions are still without a subject or outside ranges
        cur.execute("SELECT COUNT(*) FROM questions WHERE subject IS NULL OR subject = ''")
        remaining = cur.fetchone()[0]
        if remaining > 0:
            print(f"WARNING: {remaining} questions still have no subject.")
            
        conn.close()
        print("Re-categorization complete.")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    rebuild_categories()
