from appl import app
from flask import Blueprint, render_template
from flask import Flask, request, g, session, redirect, url_for, send_file
from run import gt, settings, dump
page = Blueprint('admin', __name__,
                        template_folder='templates')
@page.route('/admin', methods = ['GET', 'POST'])
def admin():

	add_tag = None
	error_message = None
	if 'login' not in session:
		return redirect(url_for('index.index'))

	if gt.get_user_status(session['login']) != 'admin':
		return '<h1>Permission Denied</h1>'

	if request.method == "POST":
		print(request.form)
		action = list(request.form.keys())[0]

		if action == 'add_tag':
			add_tag = True

		elif action == 'save_tag':
			tag = list(request.form.values())[1]

			if tag in settings['tags']:
				error_message = 'Tag {} already exists!'.format(tag)

			else:
				settings['tags'].append(tag)
				dump()

		elif action == 'del_tag':
			tag = list(request.form.values())[1]
			if tag in settings['tags']:
				settings['tags'].pop(settings['tags'].index(tag))
				dump()
			else:
				error_message = "Tag {} doesn't exitst".format(tag)

		elif action == 'change_size_val':
			size = request.form['change_size_val']
			try:
				settings['max_file_size'] = int(size) * 1024 * 1024
				dump()
			except:
				error_message = 'Enter valid number'

		elif action == 'change_count_val':
			count = request.form['change_count_val']
			try:
				settings['max_files_count'] = int(count)
				dump()
			except:
				error_message = 'Enter valid number'


	return render_template("admin.html", 
		tags = settings['tags'], 
		current_limit = settings['max_file_size']/1024/1024, 
		current_count_limit = settings['max_files_count'],
		add_tag = add_tag,
		error_message = error_message)