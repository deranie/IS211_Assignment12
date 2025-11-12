from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(__file__), 'students.db')


# DATABASE CONNECTION 
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


#HOME
@app.route('/')
def index():
    return render_template('index.html')


# STUDENTS
@app.route('/students')
def view_students():
    db = get_db()
    students = db.execute('SELECT * FROM students').fetchall()
    return render_template('add_student.html', students=students)


@app.route('/add_student', methods=['POST'])
def add_student():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    db = get_db()
    db.execute('INSERT INTO students (first_name, last_name) VALUES (?, ?)', (first_name, last_name))
    db.commit()
    return redirect(url_for('view_students'))


@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    db = get_db()
    db.execute('DELETE FROM results WHERE student_id = ?', (student_id,))
    db.execute('DELETE FROM students WHERE id = ?', (student_id,))
    db.commit()
    return redirect(url_for('view_students'))


#QUIZZES
@app.route('/quizzes')
def view_quizzes():
    db = get_db()
    quizzes = db.execute('SELECT * FROM quizzes').fetchall()
    return render_template('add_quiz.html', quizzes=quizzes)


@app.route('/add_quiz', methods=['POST'])
def add_quiz():
    subject = request.form['subject']
    num_questions = request.form['num_questions']
    quiz_date = request.form['quiz_date']
    db = get_db()
    db.execute('INSERT INTO quizzes (subject, num_questions, quiz_date) VALUES (?, ?, ?)',
               (subject, num_questions, quiz_date))
    db.commit()
    return redirect(url_for('view_quizzes'))


@app.route('/delete_quiz/<int:quiz_id>')
def delete_quiz(quiz_id):
    db = get_db()
    db.execute('DELETE FROM results WHERE quiz_id = ?', (quiz_id,))
    db.execute('DELETE FROM quizzes WHERE id = ?', (quiz_id,))
    db.commit()
    return redirect(url_for('view_quizzes'))


#RESULTS
@app.route('/results')
def view_results():
    db = get_db()
    results = db.execute('''
        SELECT r.id, s.first_name, s.last_name, q.subject, q.quiz_date, r.score
        FROM results r
        JOIN students s ON r.student_id = s.id
        JOIN quizzes q ON r.quiz_id = q.id
        ORDER BY q.quiz_date DESC
    ''').fetchall()
    return render_template('view_results.html', results=results)


@app.route('/add_result_page')
def add_result_page():
    db = get_db()
    students = db.execute('SELECT * FROM students').fetchall()
    quizzes = db.execute('SELECT * FROM quizzes').fetchall()
    return render_template('add_result.html', students=students, quizzes=quizzes)


@app.route('/add_result', methods=['POST'])
def add_result():
    student_id = request.form['student_id']
    quiz_id = request.form['quiz_id']
    score = request.form['score']
    db = get_db()
    db.execute('INSERT INTO results (student_id, quiz_id, score) VALUES (?, ?, ?)',
               (student_id, quiz_id, score))
    db.commit()
    return redirect(url_for('view_results'))


@app.route('/delete_result/<int:result_id>')
def delete_result(result_id):
    db = get_db()
    db.execute('DELETE FROM results WHERE id = ?', (result_id,))
    db.commit()
    return redirect(url_for('view_results'))


@app.route('/edit_result/<int:result_id>', methods=['GET', 'POST'])
def edit_result(result_id):
    db = get_db()
    if request.method == 'POST':
        new_score = request.form['score']
        db.execute('UPDATE results SET score = ? WHERE id = ?', (new_score, result_id))
        db.commit()
        return redirect(url_for('view_results'))
    else:
        result = db.execute('''
            SELECT r.id, s.first_name, s.last_name, q.subject, r.score
            FROM results r
            JOIN students s ON r.student_id = s.id
            JOIN quizzes q ON r.quiz_id = q.id
            WHERE r.id = ?
        ''', (result_id,)).fetchone()
        return render_template('edit_result.html', result=result)


# RUN 
if __name__ == '__main__':
    app.run(debug=True)
