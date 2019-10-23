from _BookSys import app
from _BookSys.database import Book, User, db, get_or_create
from flask import render_template, request, redirect, url_for, flash, session

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

        if not session.get('logged_in'):
            flash("Not logged in")
            return redirect(url_for('home'))

        b = Book(title=request.form['title'],
         description=request.form['description'],
         quantity=(request.form['quantity'] or None), 
         owner=User.query.filter_by(username=session['username']).first())

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

@app.route('/logreg', methods=['POST'])
def logreg():

    if request.method == 'POST' and not hasattr(session, 'logged_in'):
        usrnm = request.form['username']

        session['logged_in'] = True
        session['username'] = get_or_create(db.session, User, username=usrnm).username
        print(session['username'])
        return redirect(url_for('home'))

@app.route('/logout', methods=['POST'])
def logout():
    # Check if user is not logged out
    if session.get('logged_in'):
        session.clear()
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))
