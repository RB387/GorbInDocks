from application import app
from application import decorators
from flask import request, session, redirect, url_for, Blueprint, render_template
from get_stats import get_stats

page = Blueprint('stats', __name__,
                        template_folder='templates')

@page.route('/statistics', methods = ['GET', 'POST'])
@decorators.login_required
@decorators.check_session
def statistics():
    data = get_stats()
    return data