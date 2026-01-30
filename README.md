# MCQ Exam Portal

A full-stack MCQ examination application built with Python Flask and SQLite.

## Features

- **Category-wise & Combined Exams**: Choose to take an exam from a specific section (e.g., Signals, General Rules) or a mixed pool of all questions.
- **Dynamic Limits**: 
  - Section-wise mode: Max 60 questions.
  - Combined mode: Max 500 questions.
- **Real-time Timer**: Auto-submission when time runs out.
- **Performance Analytics**: 
  - Instant scoring with negative marking (1 point for correct, -0.25 for wrong).
  - Detailed breakdown of correct, wrong, and skipped questions.
  - Review page with correct answers and explanations.
- **Responsive Design**: Modern, clean UI built with CSS and HTML.

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite3
- **Frontend**: Vanilla CSS, HTML5, JavaScript

## Setup and Installation

1.  **Clone the repository**:
    ```bash
    git clone <your-repository-url>
    cd mcq_exam_portal
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirement.txt
    ```

3.  **Run the application**:
    ```bash
    python app.py
    ```
    The app will be available at `http://127.0.0.1:5000`.

## Directory Structure
- `app.py`: Main Flask application server.
- `exam.db`: SQLite database containing 3300+ categorized questions.
- `static/`: CSS and Client-side JavaScript (timer logic).
- `templates/`: HTML templates (Home, Exam, Results).
