import Pyro4

uri = input("Enter the uri of the warehouse: ").strip()
booksys = Pyro4.Proxy(uri)
logged_in = False

while(True):
    inp = input("Enter command:").split()

    # e.g `auth TsimpDim`
    if inp[0] == "auth":
        res = booksys.logreg(str(inp[1]))
        print(res)
        logged_in = True

    elif inp[0] == "list":
        if inp[1] == "books":
            res = booksys.list_books()
            
            for book in res:
                print("[{id}] T|{title:35} A|{author:20} D|{description:60} Q|{quantity}".format(**book))

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
    
    elif inp == ["quit"]:
        exit()

