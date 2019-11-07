import ast, json, pika
from database import init_db, Book, User, Tracker, get_or_create
from datetime import datetime
from sqlalchemy import func

### RABBITMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

# channel.queue_delete(queue='rpc_queue') ## <!> REMOVE LATER
channel.queue_declare(queue='rpc_queue')

### CUSTOM
class BookSys(object):
    def __init__(self):
        self.user_session = {"logged_in": False}
        self.db_session = init_db()

    # New
    def reply_to_query(self, q):
        m = q["method"]

        if m == "books":
            return self.list_books()
        elif m == "trackers":
            print(self.list_trackers())
            return self.list_trackers()
        elif m == "auth":
            return self.logreg(q["param"])
        elif m == "unauth":
            return self.logout()
        elif m == "add":
            return self.add_book(**q["params"])
        elif m == "delete":
            return self.delete_book(q["param"])
        elif m == "borrow":
            return self.borrow_book(q["param"])
        elif m == "return":
            return self.return_book(q["param"])

    def logreg(self, username):
        u = get_or_create(self.db_session, User, username=username)
        self.db_session.add(u)
        self.db_session.commit()

        self.user_session['logged_in'] = True
        self.user_session['user_id'] = u.id
        self.user_session['username'] = u.username

        return {'msg':"Logged in successfully\n"}

    def logout(self):
        self.user_session['logged_in'] = False
        self.user_session['user_id'] = None
        self.user_session['username'] = None

        return {'msg':"You are now logged out\n"}

    def list_info(self):
        if self.user_session['logged_in']:
            u = self.db_session.query(User).filter_by(id=self.user_session['user_id']).first()
            return {
                "borrowed": self.db_session.query(Tracker).filter_by(user_id=u.id, returned_at=None).count(),
                "limit": u.limit
            }
        else:
            return {'err':"You need to login. Use `auth <username>`\n"}

    def list_books(self):
        return [r.as_dict() for r in self.db_session.query(Book).all()]

    def list_trackers(self):
        if self.user_session['logged_in']:
            return [t.as_dict() for t in self.db_session.query(Tracker).filter_by(user_id=self.user_session['user_id'])]
        else:
            return {'err':"You need to login. Use `auth <username>`\n"}

    def add_book(self, title, author, description, quantity):
        if self.user_session['logged_in']:

            if quantity < 0:
                return {'err':"Quantity cannot be negative\n"}
            
            if any(len(i) > 120 for i in [title, author, description]):
                return {'err':"Fields must have max. 120 characters\n"}

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

            return {'msg':"Book added\n"}
        else:
            return {'err':"You need to login. Use `auth <username>`\n"}

    def delete_book(self, book_id):
        b = self.db_session.query(Book).filter_by(id=book_id).first()

        if self.user_session['logged_in']:
            if b.owner.username == self.user_session['username']:
                self.db_session.delete(b)
                self.db_session.commit()

                return {'msg':"Book deleted.\n"}
            else:
                return {'err':"You are not the owner of this book\n"}
        else:
            return {'err':"You need to login. Use `auth <username>`\n"}

    def borrow_book(self, book_id):
        b = self.db_session.query(Book).filter_by(id=book_id).first()

        if self.user_session['logged_in']:
            if b.owner.username == self.user_session['username']:
                return {'err':"You own this book\n"}
            else:
                u = self.db_session.query(User).filter_by(id=self.user_session['user_id']).first()

                if self.db_session.query(Tracker).filter_by(user_id=u.id, returned_at=None).count() == u.limit:
                    return {'err':"Borrowing quota 100%, return some books\n"}

                if self.db_session.query(Tracker).filter_by(user_id=u.id, book_id=b.id, returned_at=None).count() > 0:
                    return {'err':"You have already borrowed this book\n"}

                if b.quantity == 0:
                    return {'err':"There are no copies left :(\n"}

                t = Tracker(book_id=b.id, user_id=u.id)

                b.quantity -= 1
                self.db_session.add(t)
                self.db_session.commit()

                return {'msg':"Borrowed book\n"}
        else:
            return {'err':"You need to login. Use `auth <username>`\n"}

    def return_book(self, book_id):
        b = self.db_session.query(Book).filter_by(id=book_id).first()
        u = self.db_session.query(User).filter_by(id=self.user_session['user_id']).first()

        if not b:
            # Object has been deleted
            t = self.db_session.query(Tracker).filter_by(user_id=u.id, book_id=None).order_by(Tracker.id.desc()).first()
            t.returned_at = datetime.now()

            self.db_session.commit()
            return {'msg':"Book was deleted. 'Returned' successfully.\n"}

        if self.user_session['logged_in']:
            if b.owner.username == self.user_session['username']:
                return {'err':"You own this book\n"}
            else:
                t = self.db_session.query(Tracker).filter_by(book_id=b.id, user_id=u.id).order_by(Tracker.id.desc()).first()
                b.quantity += 1
                t.returned_at = func.now()

                self.db_session.commit()
                return {'msg':"Book returned successfully.\n"}
        else:
            return {'err':"You need to login. Use `auth <username>`\n"}




def on_request(ch, method, props, body):
    def b_to_dict(b):
        ''' Transform bytes to dict '''

        b = b.decode('ascii')
        return ast.literal_eval(b)

    btd = b_to_dict(body)
    print(f" [-] Responding to {btd}")
    response = bs.reply_to_query(btd)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

bs = BookSys()
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()