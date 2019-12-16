from application import app
from flask import Blueprint, render_template
from flask import Flask, request, g, session, redirect, url_for, send_file
from werkzeug_utils_rus import secure_filename
from run import gt, ft, settings
from application import decorators
import gorbin_tools2

page = Blueprint('home', __name__,
                        template_folder='templates')

@page.route('/home', methods = ['GET', 'POST'])
@page.route('/home/<directory>', methods = ['GET', 'POST'])
@decorators.login_required
def home(directory = '/'):
	
	#get current directory full path
	if directory != 'shared':
		dir_tree = ft.get_dir_tree(session['login'], directory)
	else:
		dir_tree = [('shared', 'shared')]

	if dir_tree is None:
		#if got error with directory path then redirect
		return redirect(url_for('error'))


	if directory != '/' and directory != 'shared':
		if (gt.get_file(directory)['owner'] != session['login']) and not (gt.check_availability(login = session['login'], user_id = gt.get_user_id(session['login']), file_id = directory)):
			#if such user doesnt have permission to view this folder
			return '<h1>Permission Denied</h1>'

	user_file_list = ft.sort_files(list(gt.get_user_files(owner=session['login'], directory = directory)))
	upload_message, error_message = None, None
	check = None
	add_folder, add_tag = None, None
	tag_search = None

	
	if request.method == "POST":
		print(request.data)
		#if app gets file upload request
		if 'file' in request.files:
			#get list of files
			file_list = request.files.getlist('file')
			if len(file_list) > settings['max_files_count']:
				error_message =  'Exceeded file count limit (Max. {} files)'.format(settings['max_files_count'])

			else:
				#upload files one by one
				for file in file_list:
					error_code = ft.file_upload(file, session['login'], directory)
					
					if error_code[0] == 0:
						error_message =  'No selected file'
						break

					elif error_code[0] == -1:
						upload_message = 'File {} already exists'.format(error_code[1])
						break

					elif error_code[0] == -2:
						upload_message = 'File {} exceeds size limit'.format(error_code[1]) 
						break

				if error_code[0] == 1:
					upload_message = 'Uploaded!'

				#update files
				user_file_list = ft.sort_files(list(gt.get_user_files(owner=session['login'], directory = directory)))

		else:

			#get information what to do
			print(request.form)
			action = request.form.get('action')

			if action == 'logout':
				#logout user from session
				return redirect(url_for('logout.logout'))

			elif action == 'select_button':
				#open file select menu
				check = True

			elif action == 'add_tag_btn':
				tag_name = request.form.get('tags_select')
				file_id = request.form.get('get_id')
				if tag_name in settings['tags']:
					gt.add_tags(file_id, [tag_name])
					#update
					user_file_list = ft.sort_files(list(gt.get_user_files(owner=session['login'], directory = directory)))
				else:
					upload_message = "Tag {} doesn't exist".format(tag_name)

			elif action == 'tag':
				tag_search = request.form.get('get')
				user_file_list = ft.sort_files(list(gt.get_files_by_tag(tag = tag_search, owner=session['login'])))

			elif action == 'folder':
				#open folder
				return redirect(url_for('home.home', directory = request.form.get('get')))

			elif action == 'back':
				#go back to prev folder
				back_dir = gt.get_file(directory)['dir']
				return redirect(url_for('home.home', directory = back_dir if back_dir!='/' else None))

			elif action == 'dir':
				#go to selected folder
				go_dir = request.form.get('get')
				return redirect(url_for('home.home', directory = go_dir if go_dir!='/' else None))

			elif action == 'search_files':
				name = request.form.get('get_name')
				tags = request.form.get('get_tags')
				date_begin, date_end = request.form.get('get_date_from'), request.form.get('get_date_to')
				
				date_begin = gorbin_tools2.time2stamp(date_begin) if date_begin != '' else float("-inf")
				date_end = gorbin_tools2.time2stamp(date_end, plus = 1) if date_end != '' else float("inf")

				kwargs = {
					'name':name,
					'data': [date_begin, date_end],
				}

				if tags != '':
					tags = tags.split(';')
					kwargs.update({'tags':tags})

				user_file_list = ft.sort_files(gt.search_files(session['login'], **kwargs))


			elif action == 'download':
				#if user have permission
				file_data = gt.get_file(file_id = request.form.get('get'))
				error_code = ft.download_file(file_data, session['login'], directory)

				if error_code[0] == 1:
					return send_file(error_code[1], as_attachment=True)

				elif error_code[0] == 0:
					error_message = 'File not found!'

				elif error_code[0] == -1:
					error_message = 'Permission denied'

			elif action == 'delete':
				#if user have permission
				file_data = gt.get_file(file_id = request.form.get('get'))
				error_code = ft.delete_file(file_data, session['login'], directory)

				if error_code == 0:
					error_message = 'File not found'

				elif error_code == -1:
					error_message = 'Permission denied'

				#update
				user_file_list = ft.sort_files(list(gt.get_user_files(owner=session['login'], directory = directory)))

			elif action == 'multiple_file':

				action = request.form.get('get')

				if action == 'Download':
					#if we get action for multiple file download

					#get file ids
					values = list(request.form.values())
					error_code = ft.get_download_list(values, session['login'], directory)

					if error_code[0] == 1:
						return send_file(error_code[1], as_attachment=True)

					elif error_code[0] == 0:
						error_message = 'File not found!'

					elif error_code[0] == -1:
						error_message = 'Permission denied'

					elif error_code[0] == -3:
						upload_message = 'No file selected!'

				elif action == 'Delete':
				#if we get action for multiple file download

				#get file ids
					values = list(request.form.values())

					error_code = ft.delete_file_list(values, session['login'], directory)
					if error_code == 0:
						error_message = 'File not found'

					elif error_code == -1:
						error_message = 'Permission denied'

					elif error_code == -3:
						upload_message = 'No file selected!'

					#update
					user_file_list = ft.sort_files(list(gt.get_user_files(owner=session['login'], directory = directory)))

			
			elif action == 'create_folder':
				#if get action to create folder
				#gen path for new folder
				folder_name = secure_filename(request.form.get('get'))
				error_code = ft.create_folder(folder_name, session['login'], directory)

				if error_code == 0:
					upload_message = 'Folder {} already exists!'.format(folder_name)

				#update
				user_file_list = ft.sort_files(list(gt.get_user_files(owner=session['login'], directory = directory)))

	return render_template("home.html",
			files = user_file_list,
			path = directory if directory!='/' else None,
			upload_message = upload_message, error_message = error_message,
			check = check, tag_search = tag_search,
			directories = dir_tree,
			tags = settings['tags'])