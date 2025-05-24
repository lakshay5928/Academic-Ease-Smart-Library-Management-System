// Client-side form validation
document.addEventListener('DOMContentLoaded', function() {
    // Login form validation
    const loginForm = document.querySelector('form[action="/login"]');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const email = this.querySelector('#email').value;
            const password = this.querySelector('#password').value;
            
            if (!email || !password) {
                e.preventDefault();
                alert('Please fill in all fields');
            }
        });
    }
    
    // Course registration form validation
    const courseForm = document.querySelector('form[action="/course_registration"]');
    if (courseForm) {
        courseForm.addEventListener('submit', function(e) {
            const checked = this.querySelectorAll('input[name="courses"]:checked').length;
            
            if (checked === 0) {
                e.preventDefault();
                alert('Please select at least one course');
            }
        });
    }
    
    // Book search form validation
    const bookSearchForm = document.querySelector('form[action="/book_search"]');
    if (bookSearchForm) {
        bookSearchForm.addEventListener('submit', function(e) {
            const searchTerm = this.querySelector('input[name="search_term"]').value;
            
            if (!searchTerm) {
                e.preventDefault();
                alert('Please enter a search term');
            }
        });
    }
});