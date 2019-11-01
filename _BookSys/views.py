from _BookSys import app
from _BookSys.database import Book, User, Tracker, db, get_or_create
from flask import render_template, request, redirect, url_for, flash, session, Response
from datetime import datetime
from jsonrpc.backend.flask import api
import json

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
        u = User.query.filter_by(id=session['id']).first()
        borrowed = Tracker.query.filter_by(user_id=u.id, returned_at=None).count()
        limit = u.limit
        return render_template('database.html', users=users, books=books, trackers=trackers, borrowed=borrowed, limit = limit)
    else:
        return redirect(url_for('home'))

@api.dispatcher.add_method
def logreg(username):

    if not hasattr(session, 'logged_in'):
        user = get_or_create(db.session, User, username=username)

        session['logged_in'] = True
        session['username'] = user.username
        session['id'] = user.id

        flash("Logged in")
    else:
        flash("Already logged in")


@api.dispatcher.add_method
def logout():
    session.clear()
    flash("Logged out")

@api.dispatcher.add_method
def addbook(title, description, author, quantity):
        
    if not title:
        flash("No title given")
        return redirect(url_for('home'))

    if not session.get('logged_in'):
        flash("Not logged in")
        return redirect(url_for('home'))

    if quantity and int(quantity) < 0:
        flash("Quantity cannot be negative")
        return redirect(url_for('home'))

    b = Book(title=title.strip(),
        description=description.strip(),
        author=(author.strip() or None),
        quantity=(quantity.strip() or None), 
        owner=User.query.filter_by(username=session['username']).first())

    db.session.add(b)
    db.session.commit()

    flash("Added book")
    return "Added book"

@api.dispatcher.add_method
def delete(book_id):
            
    b = Book.query.filter_by(id=int(book_id)).first()

    if session.get('logged_in'):
        print(b.owner.username)
        if b.owner.username == session['username']:
            db.session.delete(b)
            db.session.commit()
        else:
            flash("No owneship over book")
            return "No ownership over book"
    else:
        flash("Not logged in")
        return "Not logged in"


@api.dispatcher.add_method
def borrow_book(book_id):

    b = Book.query.filter_by(id=book_id).first()

    if session.get('logged_in'):
        if b.owner.username == session['username']:
            flash("You have ownership over book")
            return 
        else:
            u = User.query.filter_by(id=session['id']).first()

            if Tracker.query.filter_by(user_id=u.id, returned_at=None).count() == u.limit:
                return "Borrowing quota 100%, return some books"

            if Tracker.query.filter_by(user_id=u.id, book_id=b.id, returned_at=None).count() > 0:
                return "You have already borrowed this book"


            t = Tracker(book_id=b.id, user_id=u.id)

            b.quantity -= 1
            db.session.add(t)
            db.session.commit()
    else:
        flash("Not logged in")
        return "Not logged in"


@api.dispatcher.add_method
def return_book(book_id, title, author):

    b = Book.query.filter_by(id=book_id).first()
    u = User.query.filter_by(id=session['id']).first()

    if not b:
        # Object has been deleted
        # Add new instance with borrowee as owner
        new_book = Book(title=title,
            author=(author or None),
            owner=u
        )

        db.session.add(new_book)

        t = Tracker.query.filter_by(user_id=u.id, book_id=None).order_by(Tracker.id.desc()).first()
        t.book = new_book
        t.returned_at = datetime.now()

        db.session.commit()
        flash("Returned book")
        return "Returned book"

    if session.get('logged_in'):
        if b.owner.username == session['username']:
            flash("You have ownership over book")
            return "You have ownership over book"
        else:
            u = User.query.filter_by(id=session['id']).first()
            t = Tracker.query.filter_by(book_id=b.id, user_id=u.id).order_by(Tracker.id.desc()).first()

            b.quantity += 1
            

            t.returned_at = datetime.now()

            db.session.commit()
            flash("Returned book")
            return "Returned book"
    else:
        flash("Not logged in")
        return "Not logged in"

