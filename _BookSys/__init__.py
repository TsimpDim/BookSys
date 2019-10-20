from flask import Flask

app = Flask(__name__)

import _BookSys.views
from _BookSys.database import init_db
init_db()