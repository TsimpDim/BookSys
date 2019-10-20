from _BookSys import app
from _BookSys.database import Book
from flask import render_template


@app.route('/')
def index():
    books = Book.query.all()
    return render_template('home.html', books=books)