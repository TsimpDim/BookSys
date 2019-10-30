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