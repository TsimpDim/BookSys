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

        return "Logged in successfully"

    def list_books(self):
        return [r.as_dict() for r in self.db_session.query(Book).all()]

    def list_trackers(self):
        return self.db_session.query(Tracker).all()

    def add_book(self, title, author, description, quantity):
        if self.user_session['logged_in']:
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

            return "Book added"
        else:
            return "You need to login. Use `auth <username>`"

def main():
    bs = BookSys()
    Pyro4.Daemon.serveSimple(
            {
                bs: "booksys"
            },
            ns=False)
            
if __name__=="__main__":
    main()