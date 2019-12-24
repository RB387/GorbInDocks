from flask import session, redirect, url_for, g
from run import gt, ft, settings
from functools import wraps
import gorbin_tools2

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if gt.get_user_status(session.get('login')) != 'admin':
            return '<h1>Permission Denied</h1>'
        else:
            return fn(*args, **kwargs)
    return wrapper

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'login' not in session:
            return redirect(url_for('index.index'))
        else:
            return fn(*args, **kwargs)
    return wrapper

def check_session(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not gt.get_user(session['login'], session['current_password']):
            return redirect(url_for('logout.logout'))
        else:
            return fn(*args, **kwargs)
    return wrapper