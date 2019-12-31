from application import app
from flask import Blueprint, render_template
from flask import request, session, redirect, url_for
from run import gt, settings, dump
from config import CONFIG_PATH
from application import decorators
import os
import shutil

page = Blueprint('admin', __name__,
                        template_folder='templates')

@page.route('/admin', methods = ['GET', 'POST'])
@decorators.login_required
@decorators.check_session
@decorators.admin_required
def admin():
	'''Admin page

		no arguments
		
		returns rendered template of page
	'''

	# initialize variables
	add_tag = None
	error_message = None

	if request.method == "POST":
		# get info what to do
		action = request.form.get('action')
		print(request.form)
		if action == 'add_tag':
			add_tag = True

		elif action == 'save_tag':
			tag = request.form.get('tag_name')
			# if such tag already exists
			if tag in settings['tags']:
				error_message = 'Tag {} already exists!'.format(tag)
			elif ';' in  tag:
				error_message = '";" is not allowed to use in tag name'
			else:
				#append and dump json config file
				settings['tags'].append(tag)
				dump(CONFIG_PATH, settings)

		elif action == 'del_tag':
			tag = request.form.get('tags')
			#if such tag exists
			if tag in settings['tags']:
				# delete it and dump json config file
				settings['tags'].pop(settings['tags'].index(tag))
				dump(CONFIG_PATH, settings)
			else:
				error_message = "Tag {} doesn't exitst".format(tag)

		elif action == 'change_size_val':
			# get new max file size
			size = request.form.get('change_size_val')
			try:
				# try to convert it and dump to json config file
				settings['max_file_size'] = int(size) * 1024 * 1024
				dump(CONFIG_PATH, settings)
			except:
				error_message = 'Enter valid number'

		elif action == 'change_count_val':
			# get new max files count in 1 upload
			count = request.form.get('change_count_val')
			try:
				# try to convert it and dump to json config file
				settings['max_files_count'] = int(count)
				dump(CONFIG_PATH, settings)
			except:
				error_message = 'Enter valid number'
		
		elif action == 'dashboard':
			return redirect(url_for('stats.dashboard'))
		
		elif action == 'add_telegram':
			# get telegram login
			telegram_login = request.form.get('telegram_login')
			if telegram_login:
				# save it
				gt.set_telegram(login=session['login'], telegram = telegram_login)
			error_message = 'Telegram linked succesfully!'
		
		elif action == 'delete':
			# get file id
			file_id = request.form.get('get')
			# get data about file
			file_data = gt.get_file(file_id, deleted=True)
			if file_data:
				if os.path.exists(file_data['location']):
					#delete file from system
					if file_data['type'] == 'folder':
						shutil.rmtree(file_data['location'])
					else:
						os.remove(file_data['location'])
				# delete file from database
				gt.del_fully(file_id)
				error_message = 'File deleted succesfully'

		elif action == 'restore':
			# get file id
			file_id = request.form.get('get')
			# restore file
			gt.revert_file(file_id)
			error_message = 'File restored succesfully'
	# render template
	return render_template("admin.html", 
		tags = settings['tags'], 
		current_limit = settings['max_file_size']/1024/1024, 
		current_count_limit = settings['max_files_count'],
		add_tag = add_tag,
		error_message = error_message,
		telegram_user_login = gt.get_telegram(session['login']),
		files = gt.get_trash())