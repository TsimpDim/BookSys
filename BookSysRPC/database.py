from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session
import psycopg2
from datetime import datetime

# Use SQLite database
engine = create_engine('postgresql+psycopg2://postgres:@localhost/BookSys', echo=True)

# Set up Base
Base = declarative_base()

# Helper function
def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

# Declare classes
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    limit = Column(Integer, default=3)

    def __repr__(self):
        return f'<User {self.username}>'

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    title = Column(String(120), unique=False, nullable=False)
    author = Column(String(120), unique=False, nullable=True)
    description = Column(String(120), unique=False, nullable=True)
    quantity = Column(Integer, default=1)
    
    owner_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    owner = relationship('User', backref=backref('book', lazy=True))

    def __repr__(self):
        return f'<Book {self.title}>'

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Tracker(Base):
    __tablename__ = 'tracker'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    book_id = Column(Integer, ForeignKey('book.id'))

    user = relationship('User', backref=backref('trackers'))
    book = relationship('Book', backref=backref('trackers'))

    borrowed_at = Column(Date, default=datetime.now)
    returned_at = Column(Date)

    def as_dict(self):
        as_dict =  {c.name: getattr(self, c.name) for c in self.__table__.columns}

        if isinstance(as_dict, list): 
            for d in as_dict:
                d['borrowed_at'] = d['borrowed_at'].strftime("%Y-%m-%d")
                if d['returned_at']: d['returned_at'] = d['returned_at'].strftime("%Y-%m-%d")
        else:
                as_dict['borrowed_at'] = as_dict['borrowed_at'].strftime("%Y-%m-%d")
                if as_dict['returned_at']: as_dict['returned_at'] = as_dict['returned_at'].strftime("%Y-%m-%d")

        return as_dict

def init_db():
    # CREATE table
    Base.metadata.create_all(engine)

    # Create session to talk to the DB
    session_factory = sessionmaker(bind=engine)

    # Scoped session so that each client has a different session
    Session = scoped_session(session_factory)

    # Create Session instance
    session = Session()

    # Create user
    def_user = get_or_create(session, User, username="default", limit="999")

    # Add user to our DB
    session.add(def_user)
    session.commit()

    return session