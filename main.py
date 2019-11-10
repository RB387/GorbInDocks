'''
Coded by RB387
'''

from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, g, session, redirect, url_for, send_file, after_this_request
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
	while directory['dir'] != '/':
		directory = gt.get_file(g, directory['dir'])
		dir_names.append((directory['_id'], directory['name']))
	print(dir_names)
	return dir_names[::-1]

@app.route('/home', methods = ['GET', 'POST'])
@app.route('/home/<directory>', methods = ['GET', 'POST'])
def home(directory = '/'): 
	print(directory)

	if 'login' in session:
		if directory != '/':
			if gt.get_file(g, directory)['owner'] != session['login']:
				return '<h1>Permission Denied</h1>'

		if request.method == "POST":
			#if app gets file upload request
			if 'file' in request.files:
				#get list of files
				file_list = request.files.getlist('file')
				#upload files one by one
				for file in file_list:
					if file.filename == '':
						return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
								error = True, error_message = 'No selected file',
								path = directory if directory!='/' else None,
								directories = get_dir_tree(directory))
					elif file:
						#get file name
						filename = secure_filename(file.filename)
						#get path where file will be saved
						file_path = os.path.join(app.config['UPLOAD_FOLDER'], session['login'])
						#create directory
						if not os.path.exists(file_path):
							os.makedirs(file_path)
						#save file
						if directory != '/':
							file_path = gt.get_file(g, directory)['location']
							print(file_path)
						else:
							file_path = os.path.join(app.config['UPLOAD_FOLDER'], session['login'])

						file_path = os.path.join(file_path, filename)
						#if file file with same name already exists
						if os.path.exists(file_path):
							#print error
							return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
								upload = True, upload_message = 'File ' + filename + ' already exists', 
								path = directory if directory!='/' else None,
								directories = get_dir_tree(directory))
						file.save(file_path)
						#"reset" fd to the beginning of the file
						file.seek(0)
						#get file size
						file_bytes = file.read()
						file.close()
						#add information about file in to database
						gt.add_file(g, owner=session['login'], name=filename, size = round(len(file_bytes)/1024/1024, 2), location = file_path, directory = str(directory))
				#refresh page
				return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
								upload = True, upload_message = 'Uploaded!',
								path = directory if directory!='/' else None,
								directories = get_dir_tree(directory))
			else:
				#get information what to do

				data =  dict(request.form)
				action = list(data.keys())[0]
				print(data)
				print(action)

				if action == 'logout':
					#logout user from session
					return redirect(url_for('logout'))

				elif action == 'select_button':
					return render_template('home.html', directory = directory,
								files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
								check = True,
								path = directory if directory!='/' else None,
								directories = get_dir_tree(directory))

				elif action == 'add_folder':
					return render_template('home.html',
								files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
								add_folder = True,
								path = directory if directory!='/' else None,
								directories = get_dir_tree(directory))

				elif action[:-1:] == 'folder':
					return redirect(url_for('home', directory = data[action]))

				elif action == 'back':
					back_dir = gt.get_file(g, directory)['dir']
					return redirect(url_for('home', directory = back_dir if back_dir!='/' else None))

				elif action[:3:] == 'dir':
					return redirect(url_for('home', directory = data[action] if data[action]!='/' else None))

				else:
					#get information about file
					info = action.split()
					if len(info) == 2:
						print('in')
						action, file_id = info[0], info[1]
						file_data = gt.get_file(g, file_id = file_id)
					else:
						action = info[0]

					if action == 'download':
						#if user have permission
						if file_data:
							if session['login'] == file_data['owner']:
								#if file disappeared
								if not os.path.exists(file_data['location']):
									#delete file and print error
									gt.del_file(g, _id = file_data['_id'])
									return render_template("home.html",
										files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
										error = True, error_message = 'File not found!',
										path = directory if directory!='/' else None,
										directories = get_dir_tree(directory)) 
								#else
								if file_data['type'] == 'folder':
									if not os.path.exists(app.config['ZIP_FOLDER']):
										os.makedirs(app.config['ZIP_FOLDER'])
									temp_path = os.path.join(app.config['ZIP_FOLDER'], gt.str_now().replace(' ', '_').replace(':', '-')) + '_' + session['login'] + '.zip'

									with ZipFile(temp_path,'w') as zip: 
										if directory == '/':
											basename = os.path.join(app.config['UPLOAD_FOLDER'], session['login'])
										else:
											basename = os.path.dirname(file_data['location'])

										files_location = get_file_paths(basename)
										
										# writing each file one by one 
										for file_loc in files_location:
											zip.write(file_loc, os.path.relpath(file_loc, basename))

									

									return send_file(temp_path, as_attachment=True)

								else:
									return send_file(file_data['location'], as_attachment=True)
							else:
								return render_template("home.html",
										files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
										error = True, error_message = 'Permission denied',
										path = directory if directory!='/' else None,
										directories = get_dir_tree(directory)) 

					elif action == 'download_list':
						values = list(request.form.values())
						print(request.form)
						if len(values) > 1:
							values = values[1::]
							files_location = []
							for file_id in values:
								file_data = gt.get_file(g, file_id = file_id)
								if file_data:
									if session['login'] == file_data['owner']:
										#if file disappeared
										if not os.path.exists(file_data['location']):
											#delete file and print error
											gt.del_file(g, _id = file_data['_id'])
											return render_template("home.html",
												files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
												error = True, error_message = 'File not found!',
												path = directory if directory!='/' else None,
												directories = get_dir_tree(directory)) 
										#else
										if file_data['type']=='folder':
											files_location += get_file_paths(file_data['location'])
										else:
											files_location.append(file_data['location'])
									else:
										return render_template("home.html",
												files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
												error = True, error_message = 'Permission denied',
												path = directory if directory!='/' else None,
												directories = get_dir_tree(directory))
								else:
									return render_template("home.html",
										files = list(gt.get_user_files(g, owner=session['login'], directory = directory)),
										path = directory if directory!='/' else None,
										directories = get_dir_tree(directory))
									
							if not os.path.exists(app.config['ZIP_FOLDER']):
								os.makedirs(app.config['ZIP_FOLDER'])

							temp_path = os.path.join(app.config['ZIP_FOLDER'], gt.str_now().replace(' ', '_').replace(':', '-')) + '_' + session['login'] + '.zip'
							
							with ZipFile(temp_path,'w') as zip: 
								if directory == '/':
									basename = os.path.join(app.config['UPLOAD_FOLDER'], session['login'])
								else:
									basename = os.path.dirname(gt.get_file(g, values[0])['location'])

								# writing each file one by one 
								for file_loc in files_location:
									zip.write(file_loc, os.path.relpath(file_loc, basename))


							

							return send_file(temp_path, as_attachment=True)
						else:
							return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
								upload = True, upload_message = 'No file selected!',
								path = directory if directory!='/' else None,
								directories = get_dir_tree(directory))

					elif action == 'delete':
						#if user have permission
						if file_data:
							if session['login'] == file_data['owner']:
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
									return render_template("home.html",
										files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
										error = True, error_message = 'File not found',
										path = directory if directory!='/' else None,
										directories = get_dir_tree(directory))
							else:
								return render_template("home.html",
										files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
										error = True, error_message = 'Permission denied',
										path = directory if directory!='/' else None,
										directories = get_dir_tree(directory))

					elif action == 'delete_list':
						values = list(request.form.values())
						if len(values) > 1:
							values = values[1::]
							for file_id in values:
								file_data = gt.get_file(g, file_id = file_id)
								if file_data:
									if session['login'] == file_data['owner']:
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
											return render_template("home.html",
												files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
												error = True, error_message = 'File not found',
												path = directory if directory!='/' else None,
												directories = get_dir_tree(directory))
									else:
										return render_template("home.html",
												files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
												error = True, error_message = 'Permission denied',
												path = directory if directory!='/' else None,
												directories = get_dir_tree(directory))
								else:
									return render_template("home.html",
										files = list(gt.get_user_files(g, owner=session['login'], directory = directory)),
										path = directory if directory!='/' else None,
										directories = get_dir_tree(directory))
						else:
							return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
								upload = True, upload_message = 'No file selected!',
								path = directory if directory!='/' else None,
								directories = get_dir_tree(directory))
							
					elif action == 'cancel_list':
						return render_template("home.html",
										files = list(gt.get_user_files(g, owner=session['login'], directory = directory)),
										check = False,
										path = directory if directory!='/' else None,
										directories = get_dir_tree(directory))

					elif action == 'create_folder':
						if directory != '/':
							path = os.path.join(gt.get_file(g, directory)['location'], data[action])
						else:
							path = os.path.join(app.config['UPLOAD_FOLDER'], session['login'], data[action])

						if not os.path.exists(path):
							os.makedirs(path)
							gt.add_folder(g, owner  = session['login'], name = data[action], size = None, location = path, directory = directory)
						else:
							return render_template("home.html",
								files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
								upload = True, upload_message = 'Folder ' + data[action] + ' already exists!',
								path = directory if directory!='/' else None,
								directories = get_dir_tree(directory))


		return render_template("home.html",
				files = list(gt.get_user_files(g, owner=session['login'], directory = directory)), 
				error = False,
				path = directory if directory!='/' else None,
				directories = get_dir_tree(directory))
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
			gt.remake_links(g, 'yes')
	
	app.debug = True
	if platform == 'win32':
		app.run()
	else:
		app.run(host = '0.0.0.0')
