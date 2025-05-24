def issue_book(books, book_id, serial_no, student_id):
    for book in books:
        if book['id'] == book_id and book['serial_no'] == serial_no:
            if book['available'] == '1':
                book['available'] = '0'
                book['issued_to'] = student_id
                return True, "Book issued successfully"
            else:
                return False, f"Book already issued to {book['issued_to']}"
    return False, "Book not found"


def return_book(books, book_id, serial_no):
    for book in books:
        if book['id'] == book_id and book['serial_no'] == serial_no:
            if book['available'] == '0':
                book['available'] = '1'
                issued_to = book.get('issued_to', '')
                book['issued_to'] = ''
                return True, f"Book returned successfully from student {issued_to}"
            else:
                return False, "Book was not issued"
    return False, "Book not found"


def binary_search_books(books, search_term, search_by='title'):
    sorted_books = sorted(books, key=lambda x: x[search_by].lower())
    low, high = 0, len(sorted_books) - 1
    results = []
    search_term_lower = search_term.lower()

    while low <= high:
        mid = (low + high) // 2
        current = sorted_books[mid][search_by].lower()

        if search_term_lower in current:
            results.append(sorted_books[mid])

            left = mid - 1
            while left >= 0 and search_term_lower in sorted_books[left][search_by].lower():
                results.append(sorted_books[left])
                left -= 1

            right = mid + 1
            while right < len(sorted_books) and search_term_lower in sorted_books[right][search_by].lower():
                results.append(sorted_books[right])
                right += 1

            break
        elif search_term_lower < current:
            high = mid - 1
        else:
            low = mid + 1

    return results


def schedule_courses(selected_courses):
    sorted_courses = sorted(
        selected_courses, key=lambda x: (-int(x['credits']), len(x['prerequisites']))
    )
    scheduled = []
    time_slots = set()

    for course in sorted_courses:
        if course['time_slot'] not in time_slots:
            scheduled.append(course)
            time_slots.add(course['time_slot'])

    return scheduled


def generate_timetable(scheduled_courses):
    timetable = {}
    for course in scheduled_courses:
        slot = course['time_slot']
        if slot not in timetable:
            timetable[slot] = []
        timetable[slot].append({
            'code': course['code'],
            'name': course['name'],
            'time_slot': slot
        })

    return [{'time_slot': k, 'courses': v} for k, v in timetable.items()]


def generate_weekly_timetable(scheduled_courses):
    timetable = {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}
    subject_counts = {}
    time_slots = [
        ('09:00-10:00', 'Lecture'),
        ('10:00-11:00', 'Lecture'),
        ('11:00-11:30', 'Break'),
        ('11:30-12:30', 'Lecture'),
        ('12:30-13:30', 'Lunch'),
        ('13:30-14:30', 'Lecture'),
        ('14:30-15:30', 'Lecture'),
        ('15:30-16:00', 'Break'),
        ('16:00-17:00', 'Lecture')
    ]

    for day in timetable:
        day_schedule = []
        for time_slot, slot_type in time_slots:
            if 'Break' in slot_type or 'Lunch' in slot_type:
                day_schedule.append({
                    'time': time_slot,
                    'type': slot_type,
                    'is_break': True
                })
            else:
                for course in scheduled_courses:
                    code = course['code']
                    subject_counts[code] = subject_counts.get(code, 0)
                    if subject_counts[code] < 4:
                        day_schedule.append({
                            'time': time_slot,
                            'code': code,
                            'name': course['name'],
                            'type': 'Lecture',
                            'is_break': False
                        })
                        subject_counts[code] += 1
                        break
        timetable[day] = day_schedule

    return timetable

def filter_books(books, search_term):
    if not search_term:
        return sorted(books, key=lambda x: x['title'].lower())

    search_term = search_term.lower()
    matched = [book for book in books if search_term in book['title'].lower() or search_term in book['author'].lower()]
    unmatched = [book for book in books if book not in matched]

    return sorted(matched, key=lambda x: x['title'].lower()) + sorted(unmatched, key=lambda x: x['title'].lower())
