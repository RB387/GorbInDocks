from application import app
from application import decorators
from flask import Blueprint, render_template
from flask import request, session, redirect, url_for
from run import gt
import gorbin_tools2
page = Blueprint('index', __name__,
                        template_folder='templates')

@page.route('/', methods = ['GET', 'POST'])
def index():
	if 'login' in session:
		return redirect(url_for('home.home'))
	else:
		if request.method == "POST":
			#get information from registarion form
			result = request.form
			if gt.get_user(result['login'], gorbin_tools2.hash(result['password'])):
				#log in user to session
				session['login'] = result['login']
				session['current_password'] = gorbin_tools2.hash(result['password'])
				return redirect(url_for('home.home'))
			else:
				#print error
				return render_template("index.html", bad_auth = True)
	return render_template("index.html", bad_auth = False)