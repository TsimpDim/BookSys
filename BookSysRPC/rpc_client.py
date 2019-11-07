import pika, uuid, ast

class BookSysRpcClient(object):


    def __init__(self):
        self.logged_in = False

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        def b_to_dict(b):
            ''' Transform bytes to dict '''

            b = b.decode('ascii')
            return ast.literal_eval(b)

        if self.corr_id == props.correlation_id:
            self.response = b_to_dict(body)

    # Custom
    def process_input(self):
        inp = input("Enter command:").split()

        # e.g `auth TsimpDim`
        if inp[0] == "auth":
            self.logged_in = True
            q = {"method":"auth", "param": inp[1]}

            res = booksys_rpc.call(q)
            print(res["msg"])

        elif inp[0] == "unauth":
            self.logged_in = False
            q = {"method":"unauth"}

            res = booksys_rpc.call(q)
            print(res["msg"])

        elif inp[0] == "list":
            if inp[1] == "books":
                q = {"method":"books"}
                res = booksys_rpc.call(q)

                print("{i} {t:35} {a:20} {d:60} {q:5} {o:5}".format(i="id", t="title", a="author", d="description", q="quantity", o="owner"))
                for book in res:
                    print("[{id}] {title:35} {author:20} {description:60} {quantity:5} {owner_id:5}".format(**book))
                print("\n")

            elif inp[1] == "trackers":
                if not self.logged_in:
                    print("You need to login. Use `auth <username>`\n")
                else:
                    q = {"method":"trackers"}
                    res = booksys_rpc.call(q)

                    if 'err' in res: print(res['err'])
                    else:
                        for t in res:
                            if not t['returned_at']: t['returned_at'] = '---'

                        print("{i:10} {u_i:10} {b_i:10} {b_a:15} {r_a:10}".format(i="id", u_i="user_id", b_i="book_id", b_a="borrowed_at", r_a="returned_at"))
                        for t in res:
                            print("{id:<10} {user_id:<10} {book_id:<10} {borrowed_at:15} {returned_at:10}".format(**t))    
                        print('\n')

            elif inp[1] == "info":
                if not self.logged_in:
                    print("You need to login. Use `auth <username>`\n")
                else:
                    q = {"method":"info"}
                    res = booksys_rpc.call(q)

                    if 'err' in res: print(res['err'])
                    else:
                        print(f"Borrowed: {res['borrowed']}\nLimit: {res['limit']}\n")

            elif inp[1] == "commands":
                print("Available commands:")
                print("* auth <username>")
                print("* unauth")
                print("* list <books|trackers|commands>")
                print("* add book")
                print("* delete book <book_id>")
                print("* borrow book <book_id>")
                print("* return book <book_id>\n")

        elif inp == ["add", "book"]:
            if not self.logged_in:
                print("You need to login. Use `auth <username>`\n")
            else:
                title = input("Title: ").strip()
                author = input("Author: ").strip()
                description = input("Description: ").strip()
                quantity = int(input("Quantity: ").strip())

                q = {
                    "method":"add",
                    "params": {
                        "title":title, "author":author, "description":description, "quantity":quantity
                    }
                }

                res = booksys_rpc.call(q)

                if 'err' in res: print(res['err'])
                else:
                    print(res["msg"])


        elif inp[:2] == ["delete", "book"]:
            if len(inp) == 2:
                print("No book_id specified. Command is `delete book <book_id>`\n")

            if not self.logged_in:
                print("You need to login. Use `auth <username>`\n")
            else:
                q = {"method":"delete", "param": int(inp[2])}
                res = booksys_rpc.call(q)

                if 'err' in res: print(res['err'])
                else:
                    print(res["msg"])

        elif inp[:2] == ["borrow", "book"]:
            if len(inp) == 2:
                print("No book_id specified. Command is `borrow book <book_id>`\n")

            if not self.logged_in:
                print("You need to login. Use `auth <username>`\n")
            else:
                q = {"method":"borrow", "param": int(inp[2])}
                res = booksys_rpc.call(q)

                if 'err' in res: print(res['err'])
                else:
                    print(res["msg"])

        elif inp[:2] == ["return", "book"]:
            if len(inp) == 2:
                print("No book_id specified. Command is `borrow book <book_id>`\n")

            if not self.logged_in:
                print("You need to login. Use `auth <username>`\n")
            else:
                q = {"method":"return", "param": int(inp[2])}
                res = booksys_rpc.call(q)

                if 'err' in res: print(res['err'])
                else:
                    print(res["msg"])

        elif inp == ["quit"]:
            exit()

        else:
            print("Use command 'list commands' to see all available commands\n")


    def call(self, n):
        print(f"Requesting {n}")

        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return self.response


booksys_rpc = BookSysRpcClient()

while True:
    query = booksys_rpc.process_input()
