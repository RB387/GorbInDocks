from application import app
from flask import Flask, request, g, session, redirect, url_for, send_file, Blueprint
from application import decorators
page = Blueprint('logout', __name__,
                        template_folder='templates')
@page.route('/logout')
@decorators.login_required
def logout():
	#logout user from session (test function)
	session.pop('login', None)
	return redirect(url_for('index.index'))