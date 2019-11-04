from database import init_db, Book, User, Tracker, get_or_create
import Pyro4
import os

os.environ["PYRO_LOGFILE"] = "pyro.log"
os.environ["PYRO_LOGLEVEL"] = "DEBUG"
Pyro4.config.SERIALIZER = "pickle"

@Pyro4.expose
class BookSys(object):
    def __init__(self):
        self.user_session = {"logged_in": False}
        self.db_session = init_db()
        print("BookSys started")

    def logreg(self, username):
        u = get_or_create(self.db_session, User, username=username)
        self.db_session.add(u)
        self.db_session.commit()

        self.user_session['logged_in'] = True
        self.user_session['user_id'] = u.id
        self.user_session['username'] = u.username

        return "Logged in successfully\n"

    def logout(self):
        self.user_session['logged_in'] = False
        self.user_session['user_id'] = None
        self.user_session['username'] = None

        return "You are now logged out\n"

    def list_books(self):
        return [r.as_dict() for r in self.db_session.query(Book).all()]

    def list_trackers(self):
        return self.db_session.query(Tracker).all()

    def add_book(self, title, author, description, quantity):
        if self.user_session['logged_in']:

            if quantity < 0:
                return "Quantity cannot be negative\n"
            
            if any(len(i) > 120 for i in [title, author, description]):
                return "Fields must have max. 120 characters\n"

            b = Book(
                title=title,
                author=author,
                description=description,
                quantity=quantity,
                owner=self.db_session.query(User).filter_by(
                        id=self.user_session["user_id"]
                    ).first()
            )

            self.db_session.add(b)
            self.db_session.commit()

            return "Book added\n"
        else:
            return "You need to login. Use `auth <username>`\n"

    def delete_book(self, book_id):
        b = self.db_session.query(Book).filter_by(id=book_id).first()

        if self.user_session['logged_in']:
            if b.owner.username == self.user_session['username']:
                self.db_session.delete(b)
                self.db_session.commit()

                return "Book deleted.\n"
            else:
                return "You are not the owner of this book\n"
        else:
            return "You need to login. Use `auth <username>`\n"

def main():
    bs = BookSys()
    Pyro4.Daemon.serveSimple(
            {
                bs: "booksys"
            },
            ns=False)
            
if __name__=="__main__":
    main()