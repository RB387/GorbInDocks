from flask import g
from sys import platform
from functools import wraps
import gorbin_tools2
import file_tools
import os
import json


#For first time database configuration
setup = False

with open(os.path.join(os.getcwd(), 'settings.json')) as json_data_file:
    settings = json.load(json_data_file)

def dump():
    with open(os.path.join(os.getcwd(), 'settings.json'), 'w') as outfile:
        json.dump(settings, outfile)

gt = gorbin_tools2.mongo_tools(g)
ft = file_tools.file_tools(settings, gt)

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if gt.get_user_status(session['login']) != 'admin':
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


if __name__ == '__main__':
    #For first time database configuration
    from appl import app
    app.config.from_object('config')

    if setup:
        with app.app_context():
            gt.remake_files('yes')
            gt.remake_users('yes')
            gt.remake_links('yes')
            gt.add_user(login = 'admin', pas = gorbin_tools2.hash('admin'), email = 'xd@yolo.com', status='admin')

    app.debug = True
    if platform == 'win32':
        app.run()
    else:
        app.run(host = '0.0.0.0')