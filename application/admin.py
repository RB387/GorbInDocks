from application import app
from flask import Blueprint, render_template
from flask import request, session, redirect, url_for
from run import gt, settings, dump
from application import decorators

page = Blueprint('admin', __name__,
                        template_folder='templates')

@page.route('/admin', methods = ['GET', 'POST'])
@decorators.login_required
@decorators.check_session
@decorators.admin_required
def admin():

	add_tag = None
	error_message = None

	if request.method == "POST":
		print(request.form)
		action = request.form.get('action')

		if action == 'add_tag':
			add_tag = True

		elif action == 'save_tag':
			tag = request.form.get('tag_name')
			if tag in settings['tags']:
				error_message = 'Tag {} already exists!'.format(tag)

			else:
				settings['tags'].append(tag)
				dump()

		elif action == 'del_tag':
			tag = request.form.get('tags')
			if tag in settings['tags']:
				settings['tags'].pop(settings['tags'].index(tag))
				dump()
			else:
				error_message = "Tag {} doesn't exitst".format(tag)

		elif action == 'change_size_val':
			size = request.form.get('change_size_val')
			try:
				settings['max_file_size'] = int(size) * 1024 * 1024
				dump()
			except:
				error_message = 'Enter valid number'

		elif action == 'change_count_val':
			count = request.form.get('change_count_val')
			try:
				settings['max_files_count'] = int(count)
				dump()
			except:
				error_message = 'Enter valid number'
		
		elif action == 'dashboard':
			return redirect(url_for('stats.dashboard'))

	return render_template("admin.html", 
		tags = settings['tags'], 
		current_limit = settings['max_file_size']/1024/1024, 
		current_count_limit = settings['max_files_count'],
		add_tag = add_tag,
		error_message = error_message)