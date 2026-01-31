from flask import Flask, render_template, request
import sqlite3
import random

app = Flask(__name__)
DB_PATH = "exam.db"

# Define available subjects
SUBJECTS = [
    "General Rules", "Signals", "Block Working", "Interlocking",
    "Shunting & Yard Working", "Working of Trains (General)",
    "Abnormal Working", "Accidents & Unusual Occurrences",
    "Level Crossings", "Marshalling", "Brakes", 
    "Loco Pilot / Guard Duties & Miscellaneous"
]

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_questions(limit, subject=None):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        if subject and subject != "Combined":
            cur.execute(
                "SELECT * FROM questions WHERE subject = ? ORDER BY RANDOM() LIMIT ?",
                (subject, limit)
            )
        else:
            cur.execute(
                "SELECT * FROM questions ORDER BY RANDOM() LIMIT ?",
                (limit,)
            )
            
        rows = cur.fetchall()
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
    return render_template("index.html", subjects=SUBJECTS)

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
    
    # If mode is combined, force subject to Combined regardless of what form sent
    if mode == "combined":
        subject = "Combined"

    # Enforce limits based on mode
    max_questions = 150 if subject != "Combined" else 500
    if num_questions > max_questions:
        num_questions = max_questions

    questions = get_questions(num_questions, subject)
    
    # Validation: if no questions found (e.g. DB empty or locked)
    if not questions:
        if subject != "Combined":
             return f"Error: No questions found for subject '{subject}'.", 404
        return "Error: Could not retrieve questions. Please check database.", 500

    return render_template(
        "exam.html",
        questions=questions,
        duration=duration
    )

@app.route("/submit", methods=["POST"])
def submit_exam():
    score = 0.0
    correct_count = 0
    wrong_count = 0
    skipped_count = 0
    
    # Store results for rendering
    analysis = []
    
    try:
        # Extract ALL question IDs from the hidden inputs to ensure we capture unattempted ones
        question_ids = request.form.getlist('question_ids')
        user_answers = {}
        
        # Build map of user answers
        for qid in question_ids:
            key = f"q_{qid}"
            value = request.form.get(key)
            if value:
                # Value is expected to be just the option letter "A"
                user_answers[qid] = value

        if not question_ids:
             # Fallback if no questions (shouldn't happen in normal flow)
             return render_template("result.html", score=0, total=0, analysis=[])

        # Fetch all relevant questions from DB
        conn = get_db_connection()
        cur = conn.cursor()
        placeholders = ','.join('?' for _ in question_ids)
        query = f"SELECT * FROM questions WHERE id IN ({placeholders})"
        cur.execute(query, question_ids)
        rows = cur.fetchall()
        conn.close()
        
        # Create a lookup for questions
        questions_db = {str(row["id"]): row for row in rows}
        
        for qid in question_ids:
            if qid not in questions_db:
                continue
                
            q_data = questions_db[qid]
            user_selected = user_answers.get(qid)
            correct_option = q_data["correct_option"]
            
            # Determine status
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
                status = "skipped" # Explicitly set status for unattempted
                
            # Reconstruct options for display
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
