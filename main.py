'''
Coded by RB387
'''

from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, g, session, redirect, url_for, send_file
import gorbin_tools as gt
import os



app = Flask(__name__)
app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'data')

@app.route('/home', methods = ['GET', 'POST'])
def home(): 
	if 'login' in session:
		if request.method == "POST":
			if 'file' in request.files:
				#if app gets file upload request
				file = request.files['file']
				if file.filename == '':
					return render_template("home.html",
							files = list(gt.get_user_files(g, owner=session['login'], dbname='gorbin', files_col_name='files')), 
							error = True, error_message = 'No selected file')
					return render_template
				elif file:
					#get file name
					filename = secure_filename(file.filename)
					#get path where file will be saved
					file_path = os.path.join(app.config['UPLOAD_FOLDER'], session['login'])
					#create directory
					if not os.path.exists(file_path):
						os.makedirs(file_path)
					#save file
					file_path = os.path.join(file_path, filename)
					file.save(file_path)
					#"reset" fd to the beginning of the file
					file.seek(0)
					#get file size
					file_bytes = file.read()
					file.close()
					#add information about file in to database
					gt.add_file(g, owner=session['login'], name=filename, size = len(file_bytes), location = file_path, dbname='gorbin', files_col_name='files')
					#refresh page
					return redirect(url_for('home'))
			else:
				#get information about file
				file_data = gt.get_file(g, id = list(request.form.keys())[0], dbname='gorbin', files_col_name='files')

				if session['login'] == file_data['owner']:
					return send_file(file_data['location'], as_attachment=True)
				else:
					return render_template("home.html",
							files = list(gt.get_user_files(g, owner=session['login'], dbname='gorbin', files_col_name='files')), 
							error = True, error_message = 'Permission denied') 

		return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'], dbname='gorbin', files_col_name='files')), error = False)
	else:
		return redirect(url_for('index'))

@app.route('/reg', methods = ['GET', 'POST'])
def reg(): 
	'''
	Registration function 
	'''
	if 'login' in session:
		#If such user already logged in, then redirect him to home page
		return redirect(url_for('home'))

	if request.method == "POST":
		#get information from registarion form
		result = request.form
		with app.app_context():
			#check if such login and email already taken or not
			if (not gt.check_login(g, result['login'])) and (not gt.check_email(g, result['email'])):
				#if not, then add information about new user in database
				gt.add_user(g, login = result['login'], 
								pas = gt.hash(result['password']), 
								email = result['email'])
				#log in user in session
				session['login'] = result['login']
				#redirect to home page
				return redirect(url_for('home'))
			else:
				# if current login taken 
				if gt.check_login(g, result['login']):
					#print error msg
					return render_template("reg.html", 
											error_flag = True, 
											error_message = 'This login is already taken')
				#if current email taken
				elif gt.check_email(g, result['email']):
					#print error msg
					return render_template("reg.html", 
											error_flag = True, 
											error_message = 'This email is already taken')

	return render_template("reg.html", error_flag = False)

@app.route('/logout')
def logout():
	#logout user from session (test function)
	session.pop('login', None)
	return redirect(url_for('index'))

@app.route('/', methods = ['GET', 'POST'])
def index():
	if 'login' in session:
		return redirect(url_for('home'))
	else:
		if request.method == "POST":
			#get information from registarion form
			result = request.form 
			if gt.get_user(g, result['login'], gt.hash(result['password'])):
				#log in user to session
				session['login'] = result['login']
				return redirect(url_for('home'))
			else:
				#print error
				return render_template("main.html", bad_auth = True)
	return render_template("main.html", bad_auth = False)

if __name__ == '__main__':
	app.debug = True
	app.run()