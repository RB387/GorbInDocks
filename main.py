from flask import Flask, render_template, request, g, session, redirect, url_for
import gorbin_tools as gt


app = Flask(__name__)
app.config.from_object('config')


@app.route('/home')
def home(): 
	pass

@app.route('/reg', methods = ['GET', 'POST'])
def reg(): 

	title = 'Register'
	if 'login' in session:
		return redirect(url_for('index'))
	if request.method == "POST":
		result = request.form 

		with app.app_context():
			if (not gt.check_login(g, result['login'])) and (not gt.check_email(g, result['email'])):
				gt.add_user(g, login = result['login'], pas = result['password'], email = result['email'])
				session['login'] = result['login']
				return redirect(url_for('index'))
			else:
				if gt.check_login(g, result['login']):
					return render_template("reg.html", title = title, error_flag = True, error_message = 'This login is already taken')

				elif gt.check_email(g, result['email']):
					return render_template("reg.html", title = title, error_flag = True, error_message = 'This email is already taken')

	return render_template("reg.html", title = 'Register', error_flag = False)

@app.route('/logout')
def logout():
	session.pop('login', None)
	return redirect(url_for('index'))

@app.route('/', methods = ['GET', 'POST'])
def index():
	if 'login' in session:
		return 'logged in ' + session['login']
	else:
		return '<h1>START PAGE</h1>'

if __name__ == '__main__':
	with app.app_context():
		print(gt.get_users_col(g, dbname = 'gorbin', users_col_name = 'users'))
	app.debug = True
	app.run()