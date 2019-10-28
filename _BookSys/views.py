from _BookSys import app
from _BookSys.database import Book, User, Tracker, db, get_or_create
from flask import render_template, request, redirect, url_for, flash, session
from datetime import datetime

@app.route('/')
def home():
    books = Book.query.order_by(Book.id.asc())

    if session.get('logged_in'):
        trackers = Tracker.query.filter_by(user_id=session['id']).order_by(Tracker.id.asc())
        u = User.query.filter_by(id=session['id']).first()
        borrowed = Tracker.query.filter_by(user_id=u.id, returned_at=None).count()
        limit = u.limit

        return render_template('home.html', books=books, trackers=trackers, borrowed=borrowed, limit=limit)
    else:
        return render_template('home.html', books=books)

@app.route('/database')
def database():

    if session.get('logged_in') and session['username'] == "kmarg":

        users = User.query.all()
        books = Book.query.all()
        trackers = Tracker.query.all()
        
        return render_template('database.html', users=users, books=books, trackers=trackers)
    else:
        return redirect(url_for('home'))

@app.route('/logreg', methods=['POST'])
def logreg():

    if request.method == 'POST' and not hasattr(session, 'logged_in'):
        usrnm = request.form['username']

        user = get_or_create(db.session, User, username=usrnm)

        session['logged_in'] = True
        session['username'] = user.username
        session['id'] = user.id
        return redirect(url_for('home'))

@app.route('/logout', methods=['POST'])
def logout():
    # Check if user is not logged out
    if session.get('logged_in'):
        session.clear()
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

@app.route('/add_book', methods=['POST'])
def create():

    if request.method == 'POST':
        
        if not request.form['title']:
            flash("No title given")
            return redirect(url_for('home'))

        if not session.get('logged_in'):
            flash("Not logged in")
            return redirect(url_for('home'))

        if request.form['quantity'] and int(request.form['quantity']) < 0:
            flash("Quantity cannot be negative")
            return redirect(url_for('home'))

        b = Book(title=request.form['title'],
         description=request.form['description'],
         author=(request.form['author'] or None),
         quantity=(request.form['quantity'] or None), 
         owner=User.query.filter_by(username=session['username']).first())

        db.session.add(b)
        db.session.commit()

        return redirect(url_for('home'))

@app.route('/del_book', methods=['POST'])
def delete():

    if request.method == 'POST':
            
        b = Book.query.filter_by(id=request.form['id']).first()

        if session.get('logged_in'):
            if b.owner.username == session['username']:
                db.session.delete(b)
                db.session.commit()
            else:
                flash("No ownership over book")
                return redirect(url_for('home'))
        else:
            flash("Not logged in")
            return redirect(url_for('home'))

    return redirect(url_for('home'))


@app.route('/borrow_book', methods=['POST'])
def borrow_book():

    if request.method == 'POST':
            
        b = Book.query.filter_by(id=request.form['id']).first()

        if session.get('logged_in'):
            if b.owner.username == session['username']:
                flash("You have ownership over book")
                return redirect(url_for('home'))
            else:
                u = User.query.filter_by(id=session['id']).first()

                if Tracker.query.filter_by(user_id=u.id, returned_at=None).count() == u.limit:
                    flash("Borrowing quota 100%, return some books")
                    return redirect(url_for('home'))

                if Tracker.query.filter_by(user_id=u.id, book_id=b.id, returned_at=None).count() > 0:
                    flash("You have already borrowed this book")
                    return redirect(url_for('home'))


                t = Tracker(book_id=b.id, user_id=u.id)

                b.quantity -= 1
                db.session.add(t)
                db.session.commit()
        else:
            flash("Not logged in")
            return redirect(url_for('home'))

    return redirect(url_for('home'))

@app.route('/return_book', methods=['POST'])
def return_book():

    if request.method == 'POST':

        b = Book.query.filter_by(id=request.form['id']).first()
        u = User.query.filter_by(id=session['id']).first()

        if not b:
            # Object has been deleted
            # Add new instance with borrowee as owner
            new_book = Book(title=request.form['title'],
             author=(request.form['author'] or None),
             owner=u
            )

            db.session.add(new_book)

            t = Tracker.query.filter_by(user_id=u.id, book_id=None).order_by(Tracker.id.desc()).first()
            t.book = new_book
            t.returned_at = datetime.now()

            db.session.commit()
            return redirect(url_for('home'))

        if session.get('logged_in'):
            if b.owner.username == session['username']:
                flash("You have ownership over book")
                return redirect(url_for('home'))
            else:
                u = User.query.filter_by(id=session['id']).first()
                t = Tracker.query.filter_by(book_id=b.id, user_id=u.id).order_by(Tracker.id.desc()).first()

                b.quantity += 1
                

                t.returned_at = datetime.now()

                db.session.commit()
        else:
            flash("Not logged in")
            return redirect(url_for('home'))

    return redirect(url_for('home'))
