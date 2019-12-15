from appl import app
from flask import Flask, request, g, session, redirect, url_for, send_file, Blueprint
page = Blueprint('logout', __name__,
                        template_folder='templates')
@page.route('/logout')
def logout():
	#logout user from session (test function)
	session.pop('login', None)
	return redirect(url_for('index.index'))