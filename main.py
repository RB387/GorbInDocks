'''
Coded by RB387
'''

from werkzeug_utils_rus import secure_filename
from flask import Flask, render_template, request, g, session, redirect, url_for, send_file
from zipfile import ZipFile
from sys import platform
import gorbin_tools as gt
import os
import shutil



app = Flask(__name__)
app.config.from_object('config')


def get_file_paths(dirName):
  # setup file paths variable
  filePaths = []
   
  # Read all directory, subdirectories and file lists
  for root, directories, files in os.walk(dirName):
    for filename in files:
        # Create the full filepath by using os module.
        filePath = os.path.join(root, filename)
        filePaths.append(filePath)
         
  # return all paths
  return filePaths

def get_dir_tree(dirId):
	dir_names, directory = [], {'dir': dirId}
	#Walk up to home directory
	while directory['dir'] != '/':
		directory = gt.get_file(g, directory['dir'])
		#if directory exists
		if directory:
			dir_names.append((directory['_id'], directory['name']))
		else:
			#else return error
			return None
	#return list of directories (id, name)		
	return dir_names[::-1]

def file_upload(file, login, directory):
	'''ERROR CODES:
		1: File was uploaded succesfully
		0: No selected file
		-1: Such file already exists
	'''


	if file.filename == '':
		return (0, None)
	elif file:
		#get file name

		filename = secure_filename(file.filename)
		print(filename)
		#get path where file will be saved
		if directory != '/':
			file_path = gt.get_file(g, directory)['location']
			print(file_path)
		else:
			file_path = os.path.join(app.config['UPLOAD_FOLDER'], login)

		file_path = os.path.join(file_path, filename)
		#if file file with same name already exists
		if os.path.exists(file_path):
			#print error
			return (-1, filename)
			''''''
		file.save(file_path)
		#"reset" fd to the beginning of the file
		file.seek(0)
		#get file size
		file_bytes = file.read()
		file.close()
		#add information about file in to database
		gt.add_file(g, owner=login, name=filename, size = round(len(file_bytes)/1024/1024, 2), location = file_path, directory = str(directory))
		return (1, None)

def download_file(file_data, login, directory):
	'''ERROR CODES:
		1: File is ready for download
		0: Such file doesnt exist
		-1: Permission denied
	'''
	if file_data:
		if login != file_data['owner']:
			#if user doesnt have access for this file
			return (-1, None)

		#if file disappeared
		if not os.path.exists(file_data['location']):
			#delete file and print error
			gt.del_file(g, _id = file_data['_id'])
			return (0, None)
			'''return render_template("home.html",
				files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
				error = True, error_message = 'File not found!',
				path = directory if directory!='/' else None,
				directories = dir_tree) '''
		#else
		if file_data['type'] == 'folder':
			#download folder
			if not os.path.exists(app.config['ZIP_FOLDER']):
				#check temp path
				os.makedirs(app.config['ZIP_FOLDER'])

			#generate temp zip file name
			temp_path = os.path.join(app.config['ZIP_FOLDER'], gt.str_now().replace(' ', '_').replace(':', '-')) + '_' + login + '.zip'

			with ZipFile(temp_path,'w') as zip: 
				#get basename for file
				if directory == '/':
					basename = os.path.join(app.config['UPLOAD_FOLDER'], login)
				else:
					basename = os.path.dirname(file_data['location'])

				#get info about files location on hard drive
				files_location = get_file_paths(basename)
				
				# writing each file one by one 
				for file_loc in files_location:
					zip.write(file_loc, os.path.relpath(file_loc, basename))

			
			#send zip file
			return (1, temp_path)

		else:
			#download file
			return (1, file_data['location'])

def get_download_list(values, login, directory):
	'''ERROR CODES:
		1: zip is ready for download
		0: such doesnt exist
		-1: permission denied
		-2: no file
		-3: no file selected

	'''
	if len(values) <= 1:
		return (-3, None)
	#get only file ids
	values = values[1::]

	files_location = []

	for file_id in values:
		#read file info one by one
		file_data = gt.get_file(g, file_id = file_id)

		if file_data:
			if session['login'] != file_data['owner']:
				#if user doesnt have access for this file
				return (-1, None)
			#if file disappeared
			if not os.path.exists(file_data['location']):
				#delete file and print error
				gt.del_file(g, _id = file_data['_id'])
				return (0, None)
			#else
			if file_data['type']=='folder':
				#if folder then get info about all files in it
				files_location += get_file_paths(file_data['location'])
			else:
				#else just append
				files_location.append(file_data['location'])

		else:
			return (-2, None)
	

	if not os.path.exists(app.config['ZIP_FOLDER']):
		#check temp path
		os.makedirs(app.config['ZIP_FOLDER'])

	#generate temp zip file name
	temp_path = os.path.join(app.config['ZIP_FOLDER'], gt.str_now().replace(' ', '_').replace(':', '-')) + '_' + login + '.zip'
	
	with ZipFile(temp_path,'w') as zip: 
		#get basename for file
		if directory == '/':
			basename = os.path.join(app.config['UPLOAD_FOLDER'], login)
		else:
			basename = os.path.dirname(gt.get_file(g, values[0])['location'])

		# writing each file one by one 
		for file_loc in files_location:
			zip.write(file_loc, os.path.relpath(file_loc, basename))

	#send zip file
	return (1, temp_path)

def delete_file(file_data, login, directory):
	'''ERROR CODES:
		1: File was deleted succesfully
		0: File not found
		-1: Permission denied
	'''
	if file_data:
		if login == file_data['owner']:
			#if such file exists
			if os.path.exists(file_data['location']):
				#delete file from database
				gt.del_file(g, _id = file_data['_id'])
				#delete file from system
				if file_data['type'] == 'folder':
					shutil.rmtree(file_data['location'])
				else:
					os.remove(file_data['location'])
				return 1
			else:
				#delete from database
				gt.del_file(g, _id = file_id)
				return 0
		else:
			return -1

def delete_file_list(values, login, directory):
	'''ERROR CODES:
		1: Files were deleted succesfully
		0: File not found
		-1: Permission denied
		-2: No File data
		-3: No File selected
	'''
	if len(values) <= 1:
		return -3

	#get only file ids
	values = values[1::]
	for file_id in values:
		#read file info one by one
		file_data = gt.get_file(g, file_id = file_id)
		if file_data:
			if login == file_data['owner']:
				#if such file exists
				if os.path.exists(file_data['location']):
					#delete file from database
					gt.del_file(g, _id = file_id)
					#delete file from system
					if file_data['type'] == 'folder':
						shutil.rmtree(file_data['location'])
					else:
						os.remove(file_data['location'])
				else:
					#delete from database
					gt.del_file(g, _id = file_id)
					return 0
			else:
				#if user doesnt have access for this file
				return -1
		else:
			return -2

	return 1

def create_folder(folder_name, login, directory):
	'''ERROR CODES:
		1: Folder was created succesfully
		0: Such folder already exists
	'''
	if directory != '/':
		path = os.path.join(gt.get_file(g, directory)['location'], folder_name)
	else:
		path = os.path.join(app.config['UPLOAD_FOLDER'], login, folder_name)

	if not os.path.exists(path):
		#create folder on hard drive
		os.makedirs(path)
		#add information about it to MongoDB
		gt.add_folder(g, owner  = login, name = folder_name, size = None, location = path, directory = directory)
		return 1
	else:
		return 0

@app.route('/error', methods = ['GET'])
def error():
	return '<h1>404. Page not found</h1>'

@app.route('/home', methods = ['GET', 'POST'])
@app.route('/home/<directory>', methods = ['GET', 'POST'])
def home(directory = '/'): 

	if 'login' not in session:
		return redirect(url_for('index'))

	#get current directory full path
	dir_tree = get_dir_tree(directory)

	if dir_tree is None:
		#if got error with directory path then redirect
		return redirect(url_for('error'))


	if directory != '/':
		if gt.get_file(g, directory)['owner'] != session['login']:
			#if such user doesnt have permission to view this folder
			return '<h1>Permission Denied</h1>'

	if request.method == "POST":
		#if app gets file upload request
		if 'file' in request.files:
			#get list of files
			file_list = request.files.getlist('file')
			#upload files one by one
			for file in file_list:
				error_code = file_upload(file, session['login'], directory)

				if error_code[0] == 0:
					return render_template("home.html",
									files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
									error = True, error_message = 'No selected file',
									path = directory if directory!='/' else None,
									directories = dir_tree)

				elif error_code[0] == -1:
					return render_template("home.html",
									files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
									upload = True, upload_message = 'File ' + error_code[1] + ' already exists', 
									path = directory if directory!='/' else None,
									directories = dir_tree)
			#refresh page
			return render_template("home.html",
							files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
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
							files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
							check = True,
							path = directory if directory!='/' else None,
							directories = dir_tree)

			elif action == 'add_folder':
				#open add folder menu
				return render_template('home.html',
							files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
							add_folder = True,
							path = directory if directory!='/' else None,
							directories = dir_tree)

			elif action[:6] == 'folder':
				#open folder
				print(list(request.form.values()))
				return redirect(url_for('home', directory = list(request.form.values())[0]))

			elif action == 'back':
				#go back to prev folder
				back_dir = gt.get_file(g, directory)['dir']
				return redirect(url_for('home', directory = back_dir if back_dir!='/' else None))

			elif action[:3:] == 'dir':
				#go to selected folder
				go_dir = list(request.form.values())[0]
				return redirect(url_for('home', directory = go_dir if go_dir!='/' else None))

				#get information about file
			elif action == 'download':
				#if user have permission
				file_data = gt.get_file(g, file_id = list(request.form.values())[0])
				error_code = download_file(file_data, session['login'], directory)

				if error_code[0] == 1:
					return send_file(error_code[1], as_attachment=True)

				elif error_code[0] == 0:
					return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
								error = True, error_message = 'File not found!',
								path = directory if directory!='/' else None,
								directories = dir_tree) 

				elif error_code[0] == -1:
					return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
								error = True, error_message = 'Permission denied',
								path = directory if directory!='/' else None,
								directories = dir_tree)
						 

			elif action == 'download_list':
				#if we get action for multiple file download

				#get file ids
				values = list(request.form.values())
				error_code = get_download_list(values, session['login'], directory)

				if error_code[0] == 1:
					return send_file(error_code[1], as_attachment=True)

				elif error_code[0] == 0:
					return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
								error = True, error_message = 'File not found!',
								path = directory if directory!='/' else None,
								directories = dir_tree) 

				elif error_code[0] == -1:
					return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
								error = True, error_message = 'Permission denied',
								path = directory if directory!='/' else None,
								directories = dir_tree)
				elif error_code[0] == -2:
					return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'], directory = directory)),
								path = directory if directory!='/' else None,
								directories = dir_tree)
				elif error_code[0] == -3:
					return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
								upload = True, upload_message = 'No file selected!',
								path = directory if directory!='/' else None,
								directories = dir_tree)					

			elif action == 'delete':
				#if user have permission
				file_data = gt.get_file(g, file_id = list(request.form.values())[0])
				error_code = delete_file(file_data, session['login'], directory)

				if error_code == 0:
					return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
								error = True, error_message = 'File not found',
								path = directory if directory!='/' else None,
								directories = dir_tree)
				elif error_code == -1:
					return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
								error = True, error_message = 'Permission denied',
								path = directory if directory!='/' else None,
								directories = dir_tree)
						

			elif action == 'delete_list':
				#if we get action for multiple file download

				#get file ids
				values = list(request.form.values())

				error_code = delete_file_list(values, session['login'], directory)
				if error_code == 0:
					return render_template("home.html",
										files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
										error = True, error_message = 'File not found',
										path = directory if directory!='/' else None,
										directories = dir_tree) 

				elif error_code == -1:
					return render_template("home.html",
										files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
										error = True, error_message = 'Permission denied',
										path = directory if directory!='/' else None,
										directories = dir_tree)
				elif error_code == -2:
					return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'], directory = directory)),
								path = directory if directory!='/' else None,
								directories = dir_tree)
				elif error_code == -3:
					return render_template("home.html",
						files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
						upload = True, upload_message = 'No file selected!',
						path = directory if directory!='/' else None,
						directories = dir_tree)
								
			elif action == 'cancel_list':
				#cancel action
				return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'], directory = directory)),
								check = False,
								path = directory if directory!='/' else None,
								directories = dir_tree)

			elif action == 'create_folder':
				#if get action to create folder
				#gen path for new folder
				folder_name = secure_filename(list(request.form.values())[0])
				error_code = create_folder(folder_name, session['login'], directory)

				if error_code == 0:
					return render_template("home.html",
						files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
						upload = True, upload_message = 'Folder ' + folder_name + ' already exists!',
						path = directory if directory!='/' else None,
						directories = dir_tree)
					
	return render_template("home.html",
			files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
			error = False,
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
			gt.remake_links(g, 'yes')
	
	app.debug = True
	if platform == 'win32':
		app.run()
	else:
		app.run(host = '0.0.0.0')
