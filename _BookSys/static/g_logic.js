function make_rpc_req(method, params){

    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://localhost:5000/', true); // async = True
    xhr.setRequestHeader('Content-type', 'application/json'); // necessary for RPC to get actual JSON
    
    // When we get a response
    xhr.onload = function () {
        location.reload(); // Refresh the page
    };

    // Build JSON
    let json = JSON.stringify(
        {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
    );

    // Send RPC request
    xhr.send(json);
}

function logreg(){
    let usrnm = document.getElementsByName("username")[0].value;
    make_rpc_req("logreg", [usrnm]);
}

function logout(){
    make_rpc_req("logout");
}

function addBook(){
    let title = document.getElementsByName("title")[0].value;
    let author = document.getElementsByName("author")[0].value;
    let description = document.getElementsByName("description")[0].value;
    let quantity = document.getElementsByName("quantity")[0].value;

    make_rpc_req("addbook", [title, author, description, quantity]);
}

function deleteBook(id){
    make_rpc_req("delete", [id]);
}

function borrowBook(id){
    make_rpc_req("borrow_book", [id]);
}

function returnBook(id, title, author){
    make_rpc_req("return_book", [id, title, author]);
}