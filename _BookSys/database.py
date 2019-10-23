from _BookSys import app
import datetime
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://wqzocheexnukrd:c43124bfb829ade0781531a5b5dc6ebbc9c625d433a5bf050e847b33649ec713@ec2-54-246-121-32.eu-west-1.compute.amazonaws.com/d1kl95pboccuhh'
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
    title = db.Column(db.String(50), unique=False, nullable=False)
    description = db.Column(db.String(120), unique=False, nullable=True)
    quantity = db.Column(db.Integer, default=1)

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref=db.backref('books', lazy=True))

    def __repr__(self):
        return f'<Book {self.title}>'

class Tracker(db.Model):
    __tablename__ = 'tracker'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    borrowed_at = db.Column(db.Date, default=datetime.datetime.now)
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