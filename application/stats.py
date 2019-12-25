from application import app
from application import decorators
from flask import request, session, redirect, url_for, Blueprint, render_template
from get_stats import get_stats

page = Blueprint('stats', __name__,
                        template_folder='templates')

@page.route('/admin/statistics', methods = ['GET', 'POST'])
@decorators.login_required
@decorators.check_session
@decorators.admin_required
def statistics():
    data = get_stats()
    return render_template("stats.html", 
                        tags_data = list(data['overall']['tags'].items()),
                        users_data = data['users'],
                        overall = data['overall'])