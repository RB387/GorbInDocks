from flask import g, Flask
import gorbin_tools2

app = Flask(__name__)
gt = gorbin_tools2.mongo_tools(g)
if __name__ == '__main__':
    with app.app_context():
    	#Configure database
        gt.remake_files('yes')
        gt.remake_users('yes')
        #add default admin user
        gt.add_user(login = 'admin', pas = gorbin_tools2.hash('admin00'), email = 'xd@yolo.com', status='admin')

