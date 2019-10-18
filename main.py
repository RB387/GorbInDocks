####################
#	Coded by RB387 # 
####################

from flask import Flask, render_template, request, g, session, redirect, url_for
import gorbin_tools as gt


app = Flask(__name__)
app.config.from_object('config')


@app.route('/home')
def home(): 
	pass

@app.route('/reg', methods = ['GET', 'POST'])
def reg(): 
	'''
		Registration function 
	'''

	if 'login' in session:
		#If such already logged in, then redirect him to home page
		return redirect(url_for('index'))

	if request.method == "POST":
		#get information from registarion form
		result = request.form 
		with app.app_context():
			#check if such login and email already taken or not
			if (not gt.check_login(g, result['login'])) and (not gt.check_email(g, result['email'])):
				#if not, then add information about new user in database
				gt.add_user(g, login = result['login'], pas = result['password'], email = result['email'])
				#login him in session
				session['login'] = result['login']
				#redirect to home page
				return redirect(url_for('index'))
			else:
				# if current login taken 
				if gt.check_login(g, result['login']):
					#print error msg
					return render_template("reg.html", error_flag = True, error_message = 'This login is already taken')
				#if current email taken
				elif gt.check_email(g, result['email']):
					#print error msg
					return render_template("reg.html", error_flag = True, error_message = 'This email is already taken')

	return render_template("reg.html", error_flag = False)

@app.route('/logout')
def logout():
	#logout user from session (test function)
	session.pop('login', None)
	return redirect(url_for('index'))

@app.route('/', methods = ['GET', 'POST'])
def index():
	if 'login' in session:
		return 'logged in ' + session['login']
	else:
		return '<h1>START PAGE</h1>'

if __name__ == '__main__':
	app.debug = True
	app.run()