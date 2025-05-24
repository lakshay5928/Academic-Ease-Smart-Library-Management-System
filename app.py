from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
from algorithms import (
    binary_search_books,
    schedule_courses,
    generate_timetable,
    generate_weekly_timetable,
    issue_book as issue_book_logic,
    return_book as return_book_logic
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

# Routes

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

    if request.method == 'POST':
        book_id = request.form['book_id']
        serial_no = request.form['serial_no']
        success, message = issue_book_logic(books, book_id, serial_no, session['student_id'])
        flash(message, 'success' if success else 'error')

    return render_template('issue_book.html', books=books)

@app.route('/return_book', methods=['GET', 'POST'])
def return_book():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    student_id = session['student_id']
    
    # Get books issued to current student
    books_to_return = [book for book in books if book.get('issued_to') == student_id]
    
    if request.method == 'POST':
        book_id, serial_no = request.form['book_id'].split('|')
        
        # Find the book
        for book in books:
            if book['id'] == book_id and book['serial_no'] == serial_no:
                if book['available'] == '0' and book['issued_to'] == student_id:
                    book['available'] = '1'
                    book['issued_to'] = ''
                    flash('Book returned successfully!', 'success')
                    return redirect(url_for('return_book'))
                else:
                    flash('This book cannot be returned', 'danger')
                    return redirect(url_for('return_book'))
        
        flash('Book not found', 'danger')
        return redirect(url_for('return_book'))
    
    return render_template('return_book.html', books_to_return=books_to_return)
@app.route('/course_registration', methods=['GET', 'POST'])
def course_registration():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        selected_courses = request.form.getlist('courses')
        selected_course_objects = [c for c in courses if c['code'] in selected_courses]
        scheduled_courses = schedule_courses(selected_course_objects)
        session['registered_courses'] = scheduled_courses
        return redirect(url_for('timetable'))

    return render_template('course_registration.html', courses=courses)

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
    


def load_books():
    books = []
    with open('books.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            books.append(dict(row))
    return books

def save_books(books):
    with open('books.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=books[0].keys())
        writer.writeheader()
        writer.writerows(books)

@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book_route():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    from algorithms import filter_books  # Ensure this is available
    books = load_books()
    search = request.args.get('search', '').strip()
    student_id = session['student_id']

    if request.method == 'POST':
        book_id = request.form['book_id']
        serial_no = request.form['serial_no']
        success, message = issue_book_logic(books, book_id, serial_no, student_id)
        save_books(books)
        flash(message, 'success' if success else 'error')
        return redirect(url_for('issue_book_route', search=search))

    # GET request – apply search filter
    filtered_books = filter_books(books, search)

    return render_template('issue_book.html', books=filtered_books)
