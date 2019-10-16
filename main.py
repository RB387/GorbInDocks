from flask import Flask, render_template, request, redirect, url_for, g
from gorbin_tools import *

app = Flask(__name__)
app.config.from_object('config')


# Lambdas for working with request.form dict
form = lambda key: request.form[key] # takes key, returns value
form_get = lambda key, ret: request.form.get(key, ret) # takes key and ret, returns value if exists or returns ret


@app.route('/home')
def home(): 
	return '<h1>YOU IN! WELCOME TO HOME!</h1>'

@app.route('/reg', methods = ['GET', 'POST'])
def reg(): 
	if request.method == "POST":
		result = request.form
		print(result)
		
		#EMPTY

	return render_template("reg.html", title = 'Register')


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods = ['POST'])
def login():
	if check_user(g, form('login'), form('password')):
		return redirect(url_for('home'))
	return render_template('login.html', bad_auth=True)

if __name__ == '__main__':
    app.debug = True
    app.run()