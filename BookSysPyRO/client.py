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
            res = booksys.list_trackers()
            print(res)
    
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

    elif inp == ["quit"]:
        exit()

