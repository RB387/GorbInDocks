from appl import app
from flask import Flask, request, g, session, redirect, url_for, send_file, Blueprint, render_template
from run import gt
import gorbin_tools2

page = Blueprint('user', __name__,
                        template_folder='templates')

@page.route('/user', methods = ['GET', 'POST'])
@page.route('/user/<user_id>', methods = ['GET', 'POST'])
def user():
	error_message = None
	if request.method == "POST":
		print(request.form)
		action = request.form.get('action')

		if action == 'change_mail':
			new_email = request.form.get('change_email_val')

			if new_email:
				if not gt.check_email(new_email):
					gt.update_user_mail(login = session['login'], email = new_email)
					error_message = 'Mail changed succesfully!'
				else:
					error_message = 'This email is already taken!'

		elif action == 'change_pass':
			old_password = request.form.get('password_val_old')
			new_password = request.form.get('change_password_val')
			if old_password and new_password:
				if gt.get_user(login = session['login'], pas = gorbin_tools2.hash(old_password)):
					gt.update_user_pass(login = session['login'], pas = gorbin_tools2.hash(new_password))
					error_message = 'Password changed succesfully!'
				else:
					error_message = 'Wrong password!'

	return render_template("user.html", 
				current_mail = gt.get_user_data(session['login'])['email'],
				error_message = error_message) 