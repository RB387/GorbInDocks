from flask import Flask, render_template, request

app = Flask(__name__)
app.config.from_object('config')


@app.route('/home')
def home(): 
	pass

@app.route('/reg', methods = ['GET', 'POST'])
def reg(): 
	if request.method == "POST":
		result = request.form
		print(result)
		
		#EMPTY

	return render_template("reg.html", title = 'Register')


@app.route('/', methods = ['GET', 'POST'])
def index():
    return '<h1>START PAGE</h1>'

if __name__ == '__main__':
    app.debug = True
    app.run()