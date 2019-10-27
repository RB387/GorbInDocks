'''
Coded by RB387
'''

from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, g, session, redirect, url_for, send_file
import gorbin_tools as gt
import os



app = Flask(__name__)
app.config.from_object('config')


@app.route('/home', methods = ['GET', 'POST'])
def home(): 
	if 'login' in session:
		if request.method == "POST":
			#if app gets file upload request
			if 'file' in request.files:
				#get list of files
				file_list = request.files.getlist('file')
				#upload files one by one
				for file in file_list:
					if file.filename == '':
						return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'])), 
								error = True, error_message = 'No selected file')
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
						#if file file with same name already exists
						if os.path.exists(file_path):
							#print error
							return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'])), 
								upload = True, upload_message = 'File ' + filename + ' already exists')
						file.save(file_path)
						#"reset" fd to the beginning of the file
						file.seek(0)
						#get file size
						file_bytes = file.read()
						file.close()
						#add information about file in to database
						gt.add_file(g, owner=session['login'], name=filename, size = round(len(file_bytes)/1024/1024, 2), location = file_path)
				#refresh page
				return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'])), 
								upload = True, upload_message = 'Uploaded!')
			else:
				#get information what to do
				action = list(request.form.keys())[0]

				if action == 'logout':
					#logout user from session
					return redirect(url_for('logout'))

				else:
					#get information about file
					action, file_id = action.split()
					file_data = gt.get_file(g, id = file_id)
					
					if action == 'download':
						print('yes')
						#if user have permission
						if file_data:
							if session['login'] == file_data['owner']:
								#if file disappeared
								if not os.path.exists(file_data['location']):
									#delete file and print error
									gt.del_file(g, _id = file_data['_id'])
									return render_template("home.html",
										files = list(gt.get_user_files(g, owner=session['login'])), 
										error = True, error_message = 'File not found!') 
								#else
								return send_file(file_data['location'], as_attachment=True)
							else:
								return render_template("home.html",
										files = list(gt.get_user_files(g, owner=session['login'])), 
										error = True, error_message = 'Permission denied') 

					elif action == 'delete':
						#if user have permission
						if file_data:
							if session['login'] == file_data['owner']:
								#if such file exists
								if os.path.exists(file_data['location']):
									#delete file from database
									gt.del_file(g, _id = file_id)
									#delete file from system
									os.remove(file_data['location'])
								else:
									#delete from database
									gt.del_file(g, _id = file_id)
									return render_template("home.html",
										files = list(gt.get_user_files(g, owner=session['login'])), 
										error = True, error_message = 'File not found')
							else:
								return render_template("home.html",
										files = list(gt.get_user_files(g, owner=session['login'])), 
										error = True, error_message = 'Permission denied')


		return render_template("home.html",
				files = list(gt.get_user_files(g, owner=session['login'])), 
				error = False)
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
	#For first time database configuration
	setup = False

	if setup:
		with app.app_context():
			gt.remake_files(g, 'yes')
			gt.remake_users(g, 'yes')
			setup = False

	app.debug = True
	app.run()