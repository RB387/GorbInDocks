from flask import Flask, url_for
from run import bot
app = Flask(__name__)
import application.admin as admin
import application.index as index
import application.home as home
import application.reg as reg
import application.logout as logout
import application.error as error
import application.user as user
import application.stats as stats

app.register_blueprint(admin.page)
app.register_blueprint(index.page)
app.register_blueprint(home.page)
app.register_blueprint(reg.page)
app.register_blueprint(logout.page)
app.register_blueprint(error.page)
app.register_blueprint(user.page)
app.register_blueprint(stats.page)

