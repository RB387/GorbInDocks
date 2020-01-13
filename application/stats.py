from application import app
from application import decorators
from flask import request, session, redirect, url_for, Blueprint, render_template
from get_stats import get_stats
from run import gt
import gorbin_tools2

page = Blueprint('stats', __name__,
                        template_folder='templates')

@page.route('/admin/dashboard', methods = ['GET', 'POST'])
@page.route('/admin/dashboard/<user_id>', methods = ['GET', 'POST'])
@decorators.login_required
@decorators.check_session
@decorators.admin_required
def dashboard(user_id=None):
    # get statistics data
    data = get_stats()
    # initialize variables
    personal_data = None
    error_message = None
    user_login = None
    # if admin views user stats
    if user_id:
        # get user stats
        personal_data = data['users'].get(user_id)
        if not personal_data:
            return '<h1>User not found</h1>'
        data['overall']['overall_files_count'] = data['users'][user_id]['files_count']
        data['overall']['overall_folders_count'] = data['users'][user_id]['folders_count']
        data['overall']['overall_size'] = data['users'][user_id]['total_size']

    if request.method == "POST":
        # get what to do
        action = request.form.get('action')
        if action == 'view_user':
            return redirect(url_for('stats.dashboard', user_id = request.form.get('get')))
        elif action == 'change_mail':
            # get new email
            new_email = request.form.get('change_email_val')
            if new_email:
                # check if such email available
                if not gt.check_email(new_email):
                    # update info
                    gt.update_user_mail(login = user_id, email = new_email)
                    error_message = 'Email was changed succesfully!'
                else:
                    error_message = 'This email is already taken!'

        elif action == 'change_pass':
            # get confirmation password
            admin_password = request.form.get('admin_password')
            # get new password
            new_password = request.form.get('change_password_val')
            if admin_password and new_password:
                # if password correct
                if gt.get_user(login = session['login'], pas = gorbin_tools2.hash(admin_password)):
                    # update info
                    gt.update_user_pass(login = user_id, pas = gorbin_tools2.hash(new_password))
                    error_message = 'Password was changed succesfully!'
                else:
                    error_message = 'Wrong password!'
        elif action == 'admin_status':
            # get confirmation password
            admin_password = request.form.get('admin_password')
            # check if password correct
            if gt.get_user(login = session['login'], pas = gorbin_tools2.hash(admin_password)):
                # update info
                gt.update_user_status(user_id, 'admin')
            else:
                error_message = 'Wrong password!'
        elif action == 'remove_admin_status':
            # get confirmation password
            admin_password = request.form.get('admin_password')
            if user_id == 'admin':
                # if such user is not reserved by system
                error_message = "You can't remove admin privileges from this user"
            # check if password correct
            elif gt.get_user(login = session['login'], pas = gorbin_tools2.hash(admin_password)):
                # update info
                gt.update_user_status(user_id, 'simple')
            else:
                error_message = 'Wrong password!'
        elif action == 'search_user':
            # get info about user
            user_login = request.form.get('user_login')
            if user_login:
                # get list of all users
                users = list(data['users'].keys())
                for user in users:
                    if user_login.lower() not in user.lower(): data['users'].pop(user)
        elif action == 'period':
            # get dates
            date_begin, date_end = request.form.get('get_date_from'), request.form.get('get_date_to')
            # formate it
            date_begin = gorbin_tools2.time2stamp(date_begin) if date_begin != '' else float("-inf")
            date_end = gorbin_tools2.time2stamp(date_end, plus = 1) if date_end != '' else float("inf")
            # get stats from to
            data = get_stats(date_begin, date_end)

        
    return render_template("stats.html", 
                        tags_data=list(data['overall']['tags'].items()),
                        users_data=data['users'],
                        overall=data['overall'],
                        user_id=user_id,
                        personal_data=personal_data,
                        status=gt.get_user_status(user_id) if user_id else None,
                        error_message=error_message,
                        search = user_login)