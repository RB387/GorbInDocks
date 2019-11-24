'''
Coded by RB387
'''

from werkzeug_utils_rus import secure_filename
from flask import Flask, render_template, request, g, session, redirect, url_for, send_file
from bson.objectid import ObjectId as obj_id
from zipfile import ZipFile
from sys import platform
import gorbin_tools2
import file_tools
import os
import shutil
import pickle

with open('settings.pickle', 'rb') as f:
	settings = pickle.load(f)

app = Flask(__name__)
app.config.from_object('config')
gt = gorbin_tools2.mongo_tools(g)
ft = file_tools.file_tools(g, settings)



@app.route('/error', methods = ['GET'])
def error():
	return '<h1>404. Page not found</h1>'
'''
@app.route('/share/<link>', methods = ['GET', 'POST'])
def share(link): 
	files = gt.get_linked(link)
	owner = files['files'][0]['owner']
	if files is None:
		return redirect(url_for('error'))
	if request.method == "POST":
		print(request.form)
		action = list(request.form.keys())[0]
		if action == 'download':
			file_data = gt.get_file(file_id = list(request.form.values())[0])
			error_code = ft.download_file(file_data, session['login'], None, True)

			if error_code[0] == 1:
				return send_file(error_code[1], as_attachment=True)

			elif error_code[0] == 0:
				return render_template("share.html",
										files = files['files'],
										link = link,
										message = 'File not found!')
		elif action == 'add_file':
			gt.add_shared(login = session['login'], user_id = gt.get_user_id(session['login']), file_ids = [list(request.form.values())[0]])

	return render_template("share.html",
			files = files['files'],
			link = link)
'''

@app.route('/admin', methods = ['GET', 'POST'])
def admin():
	pass


@app.route('/home', methods = ['GET', 'POST'])
@app.route('/home/<directory>', methods = ['GET', 'POST'])
def home(directory = '/'): 

	if 'login' not in session:
		return redirect(url_for('index'))

	#get current directory full path
	if directory != 'shared':
		dir_tree = ft.get_dir_tree(session['login'], directory)
	else:
		dir_tree = [('shared', 'shared')]
	print(dir_tree)

	if dir_tree is None:
		#if got error with directory path then redirect
		return redirect(url_for('error'))


	if directory != '/' and directory != 'shared':
		if (gt.get_file(directory)['owner'] != session['login']) and not (gt.check_availability(login = session['login'], user_id = gt.get_user_id(session['login']), file_id = directory)):
			#if such user doesnt have permission to view this folder
			return '<h1>Permission Denied</h1>'

	
	if request.method == "POST":
		#if app gets file upload request
		if 'file' in request.files:
			#get list of files
			file_list = request.files.getlist('file')
			#upload files one by one
			for file in file_list:
				error_code = ft.file_upload(file, session['login'], directory)

				if error_code[0] == 0:
					return render_template("home.html",
									files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
									error = True, error_message = 'No selected file',
									path = directory if directory!='/' else None,
									directories = dir_tree)

				elif error_code[0] == -1:
					return render_template("home.html",
									files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
									upload = True, upload_message = 'File ' + error_code[1] + ' already exists', 
									path = directory if directory!='/' else None,
									directories = dir_tree)
				elif error_code[0] == -2:
					return render_template("home.html",
									files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
									upload = True, upload_message = 'File ' + error_code[1] + ' exceeds size limit', 
									path = directory if directory!='/' else None,
									directories = dir_tree)
			#refresh page
			return render_template("home.html",
							files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
							upload = True, upload_message = 'Uploaded!',
							path = directory if directory!='/' else None,
							directories = dir_tree)
		else:

			#get information what to do
			print(request.form)
			action = list(request.form.keys())[0]

			if action == 'logout':
				#logout user from session
				return redirect(url_for('logout'))

			elif action == 'select_button':
				#open file select menu
				return render_template('home.html', directory = directory,
							files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
							check = True,
							path = directory if directory!='/' else None,
							directories = dir_tree)

			elif action == 'add_folder':
				#open add folder menu
				return render_template('home.html',
							files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
							add_folder = True,
							path = directory if directory!='/' else None,
							directories = dir_tree)

			elif action == 'add_tag_button':
				#open add folder menu
				return render_template('home.html',
							files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
							add_tag = obj_id(list(request.form.values())[0]),
							path = directory if directory!='/' else None,
							directories = dir_tree)

			elif action == 'add_tag':
				tag_name = list(request.form.values())[0]
				file_id = list(request.form.values())[1]
				gt.add_tags(file_id, [tag_name])

			elif action[:3] == 'tag':
				tag = list(request.form.values())[0]
				return render_template('home.html',
							files = list(gt.get_files_by_tag(tag = tag, owner=session['login'])), 
							tag_search = tag,
							path = directory if directory!='/' else None,
							directories = dir_tree)
			elif action[:6] == 'folder':
				#open folder
				print(list(request.form.values()))
				return redirect(url_for('home', directory = list(request.form.values())[0]))

			elif action == 'back':
				#go back to prev folder
				back_dir = gt.get_file(directory)['dir']
				return redirect(url_for('home', directory = back_dir if back_dir!='/' else None))

			elif action[:3:] == 'dir':
				#go to selected folder
				go_dir = list(request.form.values())[0]
				return redirect(url_for('home', directory = go_dir if go_dir!='/' else None))

			elif action == 'download':
				#if user have permission
				file_data = gt.get_file(file_id = list(request.form.values())[0])
				error_code = ft.download_file(file_data, session['login'], directory)

				if error_code[0] == 1:
					return send_file(error_code[1], as_attachment=True)

				elif error_code[0] == 0:
					return render_template("home.html",
								files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
								error = True, error_message = 'File not found!',
								path = directory if directory!='/' else None,
								directories = dir_tree) 

				elif error_code[0] == -1:
					return render_template("home.html",
								files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
								error = True, error_message = 'Permission denied',
								path = directory if directory!='/' else None,
								directories = dir_tree)
						 

			elif action == 'download_list':
				#if we get action for multiple file download

				#get file ids
				values = list(request.form.values())
				error_code = ft.get_download_list(values, session['login'], directory)

				if error_code[0] == 1:
					return send_file(error_code[1], as_attachment=True)

				elif error_code[0] == 0:
					return render_template("home.html",
								files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
								error = True, error_message = 'File not found!',
								path = directory if directory!='/' else None,
								directories = dir_tree) 

				elif error_code[0] == -1:
					return render_template("home.html",
								files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
								error = True, error_message = 'Permission denied',
								path = directory if directory!='/' else None,
								directories = dir_tree)
				elif error_code[0] == -2:
					return render_template("home.html",
								files = list(gt.get_user_files(owner=session['login'], directory = directory)),
								path = directory if directory!='/' else None,
								directories = dir_tree)
				elif error_code[0] == -3:
					return render_template("home.html",
								files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
								upload = True, upload_message = 'No file selected!',
								path = directory if directory!='/' else None,
								directories = dir_tree)					

			elif action == 'delete':
				#if user have permission
				file_data = gt.get_file(file_id = list(request.form.values())[0])
				error_code = ft.delete_file(file_data, session['login'], directory)

				if error_code == 0:
					return render_template("home.html",
								files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
								error = True, error_message = 'File not found',
								path = directory if directory!='/' else None,
								directories = dir_tree)
				elif error_code == -1:
					return render_template("home.html",
								files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
								error = True, error_message = 'Permission denied',
								path = directory if directory!='/' else None,
								directories = dir_tree)
						

			elif action == 'delete_list':
				#if we get action for multiple file download

				#get file ids
				values = list(request.form.values())

				error_code = ft.delete_file_list(values, session['login'], directory)
				if error_code == 0:
					return render_template("home.html",
										files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
										error = True, error_message = 'File not found',
										path = directory if directory!='/' else None,
										directories = dir_tree) 

				elif error_code == -1:
					return render_template("home.html",
										files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
										error = True, error_message = 'Permission denied',
										path = directory if directory!='/' else None,
										directories = dir_tree)
				elif error_code == -2:
					return render_template("home.html",
								files = list(gt.get_user_files(owner=session['login'], directory = directory)),
								path = directory if directory!='/' else None,
								directories = dir_tree)
				elif error_code == -3:
					return render_template("home.html",
						files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
						upload = True, upload_message = 'No file selected!',
						path = directory if directory!='/' else None,
						directories = dir_tree)

			elif action == 'create_folder':
				#if get action to create folder
				#gen path for new folder
				folder_name = secure_filename(list(request.form.values())[0])
				error_code = ft.create_folder(folder_name, session['login'], directory)

				if error_code == 0:
					return render_template("home.html",
						files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
						upload = True, upload_message = 'Folder ' + folder_name + ' already exists!',
						path = directory if directory!='/' else None,
						directories = dir_tree)
			'''
			elif action == 'share':
				file_id = list(request.form.values())[0]
				link = gt.make_link([file_id])
				return render_template("home.html",
						files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
						share_file = gt.get_file(file_id), share_link = url_for('share', link = link, _external = True),
						path = directory if directory!='/' else None,
						directories = dir_tree)'''
			'''
			elif action == 'shared_folder':
				return redirect(url_for('home', directory = 'shared'))'''
					
	if directory == 'shared':
		files = gt.get_shared(gt.get_user_id(session['login']))
		files = list(files.values())[0]

		return render_template('home.html',
							files = files if files else [], 
							path = 'shared',
							directories = dir_tree)
	else:
		return render_template("home.html",
				files = list(gt.get_user_files(owner=session['login'], directory = directory)), 
				path = directory if directory!='/' else None,
				directories = dir_tree)

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
			if (not gt.check_login(result['login'])) and (not gt.check_email(result['email'])):
				#if not, then add information about new user in database
				gt.add_user(login = result['login'], 
							pas = gorbin_tools2.hash(result['password']), 
							email = result['email'])
				#log in user in session
				session['login'] = result['login']
				#redirect to home page
				return redirect(url_for('home'))
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
			if gt.get_user(result['login'], gorbin_tools2.hash(result['password'])):
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
			gt.remake_files('yes')
			gt.remake_users('yes')
			gt.remake_links('yes')
	
	app.debug = True
	if platform == 'win32':
		app.run()
	else:
		app.run(host = '0.0.0.0')
