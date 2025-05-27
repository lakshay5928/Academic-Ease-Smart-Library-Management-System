
from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
from algorithms import (
    binary_search_books,
    filter_books,
    schedule_courses,
    generate_weekly_timetable,
    issue_book as issue_book_logic,
    return_book as return_book_logic,
    filter_courses_by_department
)

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load CSV data
def load_data():
    with open('data/students.csv', 'r') as f:
        students = list(csv.DictReader(f))

    with open('data/books.csv', 'r') as f:
        books = list(csv.DictReader(f))

    with open('data/courses.csv', 'r') as f:
        courses = list(csv.DictReader(f))

    return students, books, courses

students, books, courses = load_data()

def save_books(books):
    # Remove entries with invalid structure
    valid_books = [b for b in books if isinstance(b, dict) and None not in b and all(k is not None for k in b.keys())]

    if not valid_books:
        print("Warning: No valid books to save.")
        return

    fieldnames = valid_books[0].keys()

    with open('data/books.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for book in valid_books:
            filtered = {key: book.get(key, "") for key in fieldnames}
            writer.writerow(filtered)

@app.route('/')
def home():
    if 'student_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_id = request.form['student_id']
        password = request.form['password']
        for student in students:
            if student['id'] == student_id and student['password'] == password:
                session['student_id'] = student['id']
                session['student_name'] = student['name']
                return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', name=session['student_name'])

@app.route('/book_search', methods=['GET', 'POST'])
def book_search():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        search_term = request.form['search_term']
        search_by = request.form['search_by']
        results = binary_search_books(books, search_term, search_by)
        return render_template('book_search.html', results=results, search_term=search_term, search_by=search_by)

    return render_template('book_search.html')

@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book_route():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    student_id = session['student_id']
    search = request.args.get('search', '').strip()

    # Reload books fresh from CSV
    with open('data/books.csv', 'r', newline='', encoding='utf-8') as f:
        books_data = list(csv.DictReader(f))

    if request.method == 'POST':
        book_id = request.form['book_id']
        serial_no = request.form['serial_no']
        success, message = issue_book_logic(books_data, book_id, serial_no, student_id)
        save_books(books_data)
        flash(message, 'success' if success else 'error')
        return redirect(url_for('issue_book_route', search=search))

    filtered_books = filter_books(books_data, search)
    return render_template('issue_book.html', books=filtered_books)

@app.route('/return_book', methods=['GET', 'POST'])
def return_book():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    student_id = session['student_id']

    # Reload books from file
    with open('data/books.csv', 'r', newline='', encoding='utf-8') as f:
        books_data = list(csv.DictReader(f))

    books_to_return = [book for book in books_data if book.get('issued_to') == student_id]

    if request.method == 'POST':
        book_id, serial_no = request.form['book_id'].split('|')
        success, message = return_book_logic(books_data, book_id, serial_no)
        if success:
            save_books(books_data)
        flash(message, 'success' if success else 'danger')
        return redirect(url_for('return_book'))

    return render_template('return_book.html', books_to_return=books_to_return)

@app.route('/course_registration', methods=['GET', 'POST'])
def course_registration():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    department = request.args.get('department', '')
    filtered_courses = filter_courses_by_department(courses, department)

    if request.method == 'POST':
        selected_course_codes = request.form.getlist('courses')
        selected_courses = [c for c in courses if c['code'] in selected_course_codes]
        scheduled = schedule_courses(selected_courses)
        session['registered_courses'] = scheduled
        return redirect(url_for('timetable'))

    return render_template('course_registration.html', courses=filtered_courses, current_department=department)

@app.route('/timetable')
def timetable():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    registered_courses = session.get('registered_courses', [])
    weekly_timetable = generate_weekly_timetable(registered_courses)
    return render_template('timetable.html', timetable=weekly_timetable)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
