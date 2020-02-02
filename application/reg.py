from application import app
from application import decorators
from flask import Blueprint, render_template
from flask import request, session, redirect, url_for
from run import gt
from config import BOT_TOKEN
from push_notifications import notification
import gorbin_tools2
page = Blueprint('reg', __name__,
                        template_folder='templates')

@page.route('/reg', methods = ['GET', 'POST'])
def reg():
	'''
	Registration function
	'''
	if 'login' in session:
		#If such user already logged in, then redirect him to home page
		return redirect(url_for('home.home'))

	if request.method == "POST":
		#get information from registarion form
		result = request.form
		with app.app_context():
			#check if such login and email already taken or not
			if (not gt.check_login(result['login'])) and (not gt.check_email(result['email'])):
				#if not, then add information about new user in database
				if result['login'] == 'user':
					return render_template("reg.html",
									error_flag=True,
									error_message='This login is already taken')
				gt.add_user(login = result['login'],
							pas = gorbin_tools2.hash(result['password']),
							email = result['email'])
				if BOT_TOKEN:
					notification(user = result['login'], type_message = 'user', users = gt.get_telegrams())
				#log in user in session
				session['login'] = result['login']
				session['current_password'] = gorbin_tools2.hash(result['password'])
				#redirect to home page
				return redirect(url_for('home.home'))
			else:
				# if current login taken
				if gt.check_login(result['login']):
					#print error msg
					return render_template("reg.html",
									error_flag = True,
									error_message = 'This login is already taken')
				#if current email taken
				elif gt.check_email(result['email']):
					#print error msg
					return render_template("reg.html",
									error_flag = True,
									error_message = 'This email is already taken')

	return render_template("reg.html", error_flag = False)
