from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
import random
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
DB_PATH = "exam.db"

# Define available subjects
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
            cur.execute(query, params)
        else:
            # For combined, we also exclude
            query = f"SELECT * FROM questions WHERE 1=1{exclude_sql} ORDER BY RANDOM() LIMIT ?"
            params.append(limit)
            cur.execute(query, params)
            
        rows = cur.fetchall()
        
        # If we didn't get enough questions, it might be because we excluded too many.
        # Let's try again without exclusion if we are short on questions for a better user experience.
        if len(rows) < limit and exclude_ids:
            if subject and subject != "Combined":
                cur.execute("SELECT * FROM questions WHERE subject = ? ORDER BY RANDOM() LIMIT ?", (subject, limit))
            else:
                cur.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT ?", (limit,))
            rows = cur.fetchall()
            # If we fallback, we should tell the caller to clear session? 
            # Actually, the caller will handle the session update.
            
        conn.close()

        questions = []
        for row in rows:
            options = [
                ("A", row["option_a"]),
                ("B", row["option_b"]),
                ("C", row["option_c"]),
                ("D", row["option_d"]),
            ]
            random.shuffle(options)

            questions.append({
                "id": row["id"],
                "question": row["question"],
                "options": options,
                "correct": row["correct_option"]
            })
        return questions
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

@app.route("/")
def index():
    if 'seen_ids' not in session:
        session['seen_ids'] = []
    
    # Calculate subject-wise progress
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT subject, COUNT(*) FROM questions GROUP BY subject")
    counts_raw = cur.fetchall()
    
    # Get total per subject mapping
    total_counts = {row[0]: row[1] for row in counts_raw}
    
    # Get seen counts per subject
    seen_ids = session.get('seen_ids', [])
    seen_counts = {}
    
    if seen_ids:
        placeholders = ','.join('?' for _ in seen_ids)
        cur.execute(f"SELECT subject, COUNT(*) FROM questions WHERE id IN ({placeholders}) GROUP BY subject", seen_ids)
        seen_raw = cur.fetchall()
        seen_counts = {row[0]: row[1] for row in seen_raw}
    
    conn.close()
    
    # Prepare enriched subjects list for template
    enriched_subjects = []
    for s in SUBJECTS:
        total = total_counts.get(s, 0)
        seen = seen_counts.get(s, 0)
        enriched_subjects.append({
            'name': s,
            'total': total,
            'seen': seen,
            'percentage': round((seen/total * 100), 1) if total > 0 else 0
        })
    
    return render_template("index.html", 
                         subjects=enriched_subjects, 
                         seen_count=len(seen_ids),
                         total_questions=sum(total_counts.values()))

@app.route("/reset_progress")
def reset_progress():
    session['seen_ids'] = []
    return redirect(url_for('index'))

@app.route("/start", methods=["POST"])
def start_exam():
    try:
        num_questions = int(request.form.get("num_questions", 10))
        duration = int(request.form.get("duration", 15))
    except ValueError:
        num_questions = 10
        duration = 15

    mode = request.form.get("mode", "combined")
    subject = request.form.get("subject", "Combined")
    
    if mode == "combined":
        subject = "Combined"

    max_questions = 150 if subject != "Combined" else 500
    if num_questions > max_questions:
        num_questions = max_questions

    exclude_ids = session.get('seen_ids', [])
    questions = get_questions(num_questions, subject, exclude_ids)
    
    if not questions:
        questions = get_questions(num_questions, subject)
        
    if not questions:
        if subject != "Combined":
             return f"Error: No questions found for subject '{subject}'.", 404
        return "Error: Could not retrieve questions. Please check database.", 500

    new_ids = [q['id'] for q in questions]
    current_seen = session.get('seen_ids', [])
    updated_seen = list(set(current_seen + new_ids))
    session['seen_ids'] = updated_seen

    return render_template(
        "exam.html",
        questions=questions,
        duration=duration,
        subject=subject
    )

@app.route("/submit", methods=["POST"])
def submit_exam():
    score = 0.0
    correct_count = 0
    wrong_count = 0
    skipped_count = 0
    analysis = []
    
    try:
        question_ids = request.form.getlist('question_ids')
        flagged_ids = request.form.getlist('flagged_ids') # New: capture flagged IDs
        user_answers = {}
        
        for qid in question_ids:
            key = f"q_{qid}"
            value = request.form.get(key)
            if value:
                user_answers[qid] = value

        if not question_ids:
             return render_template("result.html", score=0, total=0, analysis=[])

        conn = get_db_connection()
        cur = conn.cursor()
        placeholders = ','.join('?' for _ in question_ids)
        query = f"SELECT * FROM questions WHERE id IN ({placeholders})"
        cur.execute(query, question_ids)
        rows = cur.fetchall()
        conn.close()
        
        questions_db = {str(row["id"]): row for row in rows}
        
        for qid in question_ids:
            if qid not in questions_db:
                continue
                
            q_data = questions_db[qid]
            user_selected = user_answers.get(qid)
            correct_option = q_data["correct_option"]
            
            is_correct = False
            status = "skipped"
            
            if user_selected:
                if user_selected == correct_option:
                    score += 1
                    correct_count += 1
                    is_correct = True
                    status = "correct"
                else:
                    score -= 0.25
                    wrong_count += 1
                    status = "wrong"
            else:
                skipped_count += 1
                status = "skipped"
                
            options_display = [
                ("A", q_data["option_a"]),
                ("B", q_data["option_b"]),
                ("C", q_data["option_c"]),
                ("D", q_data["option_d"]),
            ]
            
            analysis.append({
                "id": qid,
                "question": q_data["question"],
                "options": options_display,
                "selected": user_selected,
                "correct": correct_option,
                "is_correct": is_correct,
                "status": status,
                "flagged": qid in flagged_ids, # New property
                "explanation": f"Correct answer: {correct_option}" 
            })

    except Exception as e:
        print(f"Error calculating score: {e}")
        return "Error processing results", 400

    return render_template("result.html", 
                         score=round(score, 2), 
                         total=len(question_ids),
                         correct=correct_count,
                         wrong=wrong_count,
                         skipped=skipped_count,
                         analysis=analysis)

if __name__ == "__main__":
    app.run(debug=True)
