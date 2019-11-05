import Pyro4

uri = input("Enter the uri of the booksys: ").strip()
booksys = Pyro4.Proxy(uri)
logged_in = False

while(True):
    inp = input("Enter command:").split()

    # e.g `auth TsimpDim`
    if inp[0] == "auth":
        res = booksys.logreg(str(inp[1]))
        print(res)
        logged_in = True

    elif inp[0] == "unauth":
        res = booksys.logout()
        print(res)
        logged_in = False

    elif inp[0] == "list":
        if inp[1] == "books":
            res = booksys.list_books()
            
            print("{i} {t:35} {a:20} {d:60} {q}".format(i="id", t="title", a="author", d="description", q="quantity"))
            for book in res:
                print("[{id}] {title:35} {author:20} {description:60} {quantity}".format(**book))

        elif inp[1] == "trackers":
            if not logged_in:
                print("You need to login. Use `auth <username>`")
            else:
                res = booksys.list_trackers()

                for t in res:
                    if not t['returned_at']: t['returned_at'] = '---'

                print("{i:10} {u_i:10} {b_i:10} {b_a:15} {r_a:10}".format(i="id", u_i="user_id", b_i="book_id", b_a="borrowed_at", r_a="returned_at"))
                for t in res:
                    print("{id:<10} {user_id:<10} {book_id:<10} {borrowed_at:15} {returned_at:10}".format(**t))    

        elif inp[1] == "info":
            if not logged_in:
                print("You need to login. Use `auth <username>`")
            else:
                print(booksys.list_info())

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
        if not logged_in:
            print("You need to login. Use `auth <username>`")
        else:
            title = input("Title: ").strip()
            author = input("Author: ").strip()
            description = input("Description: ").strip()
            quantity = int(input("Quantity: ").strip())

            res = booksys.add_book(
                title=title,
                author=author,
                description=description,
                quantity=quantity
            )

            print(res)

    elif inp[:2] == ["delete", "book"]:
        if len(inp) == 2:
            print("No book_id specified. Command is `delete book <book_id>`")

        if not logged_in:
            print("You need to login. Use `auth <username>`")
        else:
            id = int(inp[2])

            res = booksys.delete_book(id)
            print(res)

    elif inp[:2] == ["borrow", "book"]:
        if len(inp) == 2:
            print("No book_id specified. Command is `borrow book <book_id>`")

        if not logged_in:
            print("You need to login. Use `auth <username>`")
        else:
            id = int(inp[2])

            res = booksys.borrow_book(id)
            print(res)

    elif inp[:2] == ["return", "book"]:
        if len(inp) == 2:
            print("No book_id specified. Command is `borrow book <book_id>`")

        if not logged_in:
            print("You need to login. Use `auth <username>`")
        else:
            id = int(inp[2])

            res = booksys.return_book(id)
            print(res)

    elif inp == ["quit"]:
        exit()

    else:
        print("Use command 'list commands' to see all available commands")

