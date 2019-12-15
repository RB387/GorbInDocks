from flask import Flask
app = Flask(__name__)
import appl.admin as admin
import appl.index as index
import appl.home as home
import appl.reg as reg
import appl.logout as logout
import appl.error as error

app.register_blueprint(admin.page)
app.register_blueprint(index.page)
app.register_blueprint(home.page)
app.register_blueprint(reg.page)
app.register_blueprint(logout.page)
app.register_blueprint(error.page)

