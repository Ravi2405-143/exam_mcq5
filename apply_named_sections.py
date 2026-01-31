import sqlite3

DB_PATH = "exam.db"

RANGES = [
    (1, 800, "G&SR Basics & Signals"),
    (801, 1200, "Block Working Manual (BWM)"),
    (1201, 1550, "Accident Manual & Disaster Mgmt"),
    (1551, 1950, "Operating Manual (OM)"),
    (1951, 2250, "Establishment & Financial Rules"),
    (2251, 2550, "Engineering & P-Way Rules"),
    (2551, 2800, "S&T (Signals & Telecomm) Rules"),
    (2801, 3000, "Carriage & Wagon (C&W) Rules"),
    (3001, 3200, "Loco Rules & Operation"),
    (3201, 3500, "Store Rules & Procedures")
]

def apply_categories():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        print("Starting categorization...")
        
        for start, end, name in RANGES:
            print(f"Assigning '{name}' to questions {start}-{end}...")
            cur.execute(
                "UPDATE questions SET subject = ? WHERE question_no BETWEEN ? AND ?",
                (name, start, end)
            )
        
        conn.commit()
        print("Categorization complete.")
        
        # Verify counts
        cur.execute("SELECT subject, COUNT(*) FROM questions GROUP BY subject")
        results = cur.fetchall()
        print("\nSummary of questions by subject:")
        for res in results:
            print(f"- {res[0]}: {res[1]}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    apply_categories()
