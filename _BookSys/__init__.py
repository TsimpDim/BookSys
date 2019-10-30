from flask import Flask
from jsonrpc.backend.flask import api

app = Flask(__name__)
app.register_blueprint(api.as_blueprint())
app.add_url_rule('/', 'api', api.as_view(), methods=['POST'])
app.config['SECRET_KEY'] = "distr_sys"

import _BookSys.views
from _BookSys.database import init_db
init_db()