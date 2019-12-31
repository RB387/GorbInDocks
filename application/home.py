from application import app
from flask import Blueprint, render_template
from flask import Flask, request, g, session, redirect, url_for, send_file
from werkzeug_utils_rus import secure_filename
from run import gt, ft, settings
from config import BOT_TOKEN
from push_notifications import notification
from application import decorators
import gorbin_tools2

page = Blueprint('home', __name__,
                        template_folder='templates')

@page.route('/home', methods = ['GET', 'POST'])
@page.route('/home/<status>', methods = ['GET', 'POST'])
@page.route('/home/<status>/<directory>', methods = ['GET', 'POST'])
@decorators.login_required
@decorators.check_session
def home(directory = '/', status = None):
	'''Home page module

		arguments
		directory ('/' by default) -- current folder directory
		status (None by default) -- current user

		returns rendered page template
	'''
	if not status or (gt.get_user_status(session.get('login')) != 'admin' and status != 'user'):
		# if non-admin user tries to view other users files
		# redirect user to his home page
		return redirect(url_for('.home', status = 'user'))

	if gt.get_user_status(session.get('login')) == 'admin' and status and status != 'user':
		# if admin tries to view other users files
		current_user = status
	else:
		# if admin tries to view his own files
		current_user = session['login']

	# get current directory full path
	dir_tree = ft.get_dir_tree(current_user, directory)

	if dir_tree is None:
		#if got error with directory path then redirect
		return redirect(url_for('error'))


	if directory != '/':
		if (gt.get_file(directory)['owner'] != current_user):
			#if such user doesnt have permission to view this folder
			return '<h1>Permission Denied</h1>'

	# Initialize all variables
	user_file_list = ft.sort_files(list(gt.get_user_files(owner=current_user, directory = directory)))
	upload_message, error_message = None, None
	check, deleted = None, None
	tag_search = None

	
	if request.method == "POST":
		#if app gets file upload request
		if 'file' in request.files:
			#get list of files
			file_list = request.files.getlist('file')
			if len(file_list) > settings['max_files_count']:
				error_message =  'Exceeded file count limit (Max. {} files)'.format(settings['max_files_count'])

			else:
				#upload files one by one
				for file in file_list:
					error_code = ft.file_upload(file, current_user, directory)
					# you can view description of every error code in file_tools.py file
					if error_code[0] == 0:
						error_message =  'No selected file'
						break

					elif error_code[0] == -1:
						error_message = 'File {} already exists'.format(error_code[1])
						break

					elif error_code[0] == -2:
						error_message = 'File {} exceeds size limit'.format(error_code[1]) 
						break

					if BOT_TOKEN:
						# if telegram bot turned on, send notification about new file to admins
						notification(user=session['login'], 
									type_message= 'file', 
									users=gt.get_telegrams(), 
									file_name=error_code[1])

				if error_code[0] == 1:
					upload_message = 'Uploaded!'

				# update files
				user_file_list = ft.sort_files(list(gt.get_user_files(owner=current_user, directory = directory)))

		else:
			# if no files
			# get information what to do
			print(request.form)
			action = request.form.get('action')

			if action == 'logout':
				# logout user from session
				return redirect(url_for('logout.logout'))

			elif action == 'select_button':
				# open file select menu
				check = True

			elif action == 'add_tag_btn':
				# get tag name and file id
				tag_name = request.form.get('tags_select')
				file_id = request.form.get('get_id')
				# if such tag exists
				if tag_name in settings['tags']:
					# add tag to list
					gt.add_tags(file_id, [tag_name])
					# update
					user_file_list = ft.sort_files(list(gt.get_user_files(owner=current_user, directory=directory)))
				else:
					error_message = "Tag {} doesn't exist".format(tag_name)

			elif action == 'tag':
				# get tag
				tag_search = request.form.get('get')
				# search files with such tag
				user_file_list = ft.sort_files(list(gt.get_files_by_tag(tag = tag_search, owner=current_user)))

			elif action == 'folder':
				# open folder
				return redirect(url_for('home.home', directory = request.form.get('get'), status = status))

			elif action == 'back':
				# go back to prev folder
				back_dir = gt.get_file(directory)['dir']
				return redirect(url_for('home.home', directory = back_dir if back_dir!='/' else None, status = status))

			elif action == 'dir':
				# go to selected folder
				go_dir = request.form.get('get')
				return redirect(url_for('home.home', directory = go_dir if go_dir!='/' else None, status = status))

			elif action == 'add_comment':
				# get file id and comment text
				file_id = request.form.get('get_id')
				comment = request.form.get('get_comment')
				# if comment is not empty save comment else None it
				comment = comment if comment != '' else None
				# add comment to files
				gt.add_comment(file_id, comment)
				# update
				user_file_list = ft.sort_files(list(gt.get_user_files(owner=current_user, directory = directory)))

			elif action == 'search_files':
				# get name, tags, dates
				name = request.form.get('get_name')
				tags = request.form.get('get_tags')
				date_begin, date_end = request.form.get('get_date_from'), request.form.get('get_date_to')
				# if date field is not empty save date else make it infinite
				date_begin = gorbin_tools2.time2stamp(date_begin) if date_begin != '' else float("-inf")
				# add +1 day to end date
				date_end = gorbin_tools2.time2stamp(date_end, plus = 1) if date_end != '' else float("inf")
				#pack args
				kwargs = {
					'name':name,
					'data': [date_begin, date_end],
				}
				# if tags fiels is not empty
				if tags != '':
					tags = tags.split(';')
					# add to args tags
					kwargs.update({'tags':tags})
				# search files and update
				user_file_list = ft.sort_files(gt.search_files(current_user, **kwargs))


			elif action == 'download':
				# get file data
				file_data = gt.get_file(file_id = request.form.get('get'))
				# run download function
				error_code = ft.download_file(file_data, current_user, directory)
				# you can view description of every error code in file_tools.py file
				if error_code[0] == 1:
					return send_file(error_code[1], as_attachment=True)

				elif error_code[0] == 0:
					error_message = 'File not found!'

				elif error_code[0] == -1:
					error_message = 'Permission denied'

			elif action == 'delete':
				# get file data
				file_data = gt.get_file(file_id = request.form.get('get'))
				# run delete funtion
				error_code = ft.delete_file(file_data, current_user, directory)
				# you can view description of every error code in file_tools.py file
				if error_code == 0:
					error_message = 'File not found'

				elif error_code == -1:
					error_message = 'Permission denied'

				#update
				user_file_list = ft.sort_files(list(gt.get_user_files(owner=current_user, directory = directory)))

			elif action == 'multiple_file':
				# if request to do something with multiple files
				# get what to do
				action = request.form.get('get')
				if action == 'Download':
					# get file ids
					values = list(request.form.values())
					# run download list function
					error_code = ft.get_download_list(values, current_user, directory)
					# you can view description of every error code in file_tools.py file
					if error_code[0] == 1:
						return send_file(error_code[1], as_attachment=True)

					elif error_code[0] == 0:
						error_message = 'File not found!'

					elif error_code[0] == -1:
						error_message = 'Permission denied'

					elif error_code[0] == -3:
						error_message = 'No file selected!'

				elif action == 'Delete':
					# get file ids
					values = list(request.form.values())
					# run delete list function
					error_code = ft.delete_file_list(values, current_user, directory)
					# you can view description of every error code in file_tools.py file
					if error_code == 0:
						error_message = 'File not found'

					elif error_code == -1:
						error_message = 'Permission denied'

					elif error_code == -3:
						error_message = 'No file selected!'
					#update
					user_file_list = ft.sort_files(list(gt.get_user_files(owner=current_user, directory = directory)))

			elif action == 'deleted_files':
				deleted = True
				user_file_list = ft.sort_files(gt.get_user_trash(owner=current_user))

			
			elif action == 'create_folder':
				#if get action to create folder
				#gen path for new folder
				folder_name = secure_filename(request.form.get('get'))
				# run create folder function
				error_code = ft.create_folder(folder_name, current_user, directory)
				# you can view description of every error code in file_tools.py file
				if error_code == 0:
					error_message = 'Folder {} already exists!'.format(folder_name)
				#update
				user_file_list = ft.sort_files(list(gt.get_user_files(owner=current_user, directory = directory)))
	#render home page
	return render_template("home.html",
			files = user_file_list,
			path = directory if directory!='/' else None,
			upload_message = upload_message, error_message = error_message,
			check = check, tag_search = tag_search,
			directories = dir_tree,
			tags = settings['tags'],
			status = status, deleted = deleted,
			stamp2str = gorbin_tools2.stamp2str)