from flask import Flask

app = Flask(__name__)

app.config['SECRET_KEY'] = "distr_sys"

import _BookSys.views
from _BookSys.database import init_db
init_db()