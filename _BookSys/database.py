from _BookSys import app
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy

#LOCALHOST: app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:@localhost/BookSys'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:@localhost/BookSys'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    limit = db.Column(db.Integer, default=3)

    def __repr__(self):
        return f'<User {self.username}>'

class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=False, nullable=False)
    author = db.Column(db.String(120), unique=False, nullable=True)
    description = db.Column(db.String(120), unique=False, nullable=True)
    quantity = db.Column(db.Integer, default=1)
    
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref=db.backref('book', lazy=True))

    def __repr__(self):
        return f'<Book {self.title}>'

class Tracker(db.Model):
    __tablename__ = 'tracker'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))

    user = db.relationship('User', backref=db.backref('trackers'))
    book = db.relationship('Book', backref=db.backref('trackers'))

    borrowed_at = db.Column(db.Date, default=datetime.now)
    returned_at = db.Column(db.Date)


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

def init_db():
    db.create_all()
    get_or_create(db.session, User, username="default", limit="999")