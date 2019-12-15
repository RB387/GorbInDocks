from appl import app
from flask import Flask, request, g, session, redirect, url_for, send_file, Blueprint
page = Blueprint('error', __name__,
                        template_folder='templates')
@app.route('/error', methods = ['GET'])
def error():
	return '<h1>404. Page not found</h1>'