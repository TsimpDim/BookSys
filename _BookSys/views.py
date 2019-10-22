from _BookSys import app
from _BookSys.database import Book, User, db
from flask import render_template, request, redirect, url_for, flash


@app.route('/')
def home():
    books = Book.query.all()
    return render_template('home.html', books=books)

@app.route('/add_book', methods=['POST'])
def create():

    if request.method == 'POST':
        
        if not request.form['title']:
            flash("No title given")
            return redirect(url_for('home'))


        b = Book(title=request.form['title'],
         description=request.form['description'],
         quantity=(request.form['quantity'] or None), 
         owner=User.query.filter_by(username='default').first())

        db.session.add(b)
        db.session.commit()

        return redirect(url_for('home'))

@app.route('/del_book', methods=['POST'])
def delete():

    if request.method == 'POST':
            
        b = Book.query.filter_by(id=request.form['id'])
        b.delete()
        db.session.commit()

        return redirect(url_for('home'))

