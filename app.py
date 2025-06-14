from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from image_capture import capture_images_for_letter
import MySQLdb.cursors
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'anonymous****'  # Enter your MySql password 
app.config['MYSQL_DB'] = 'logindetails'

mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            '''return render_template('index.html', msg='Logged in successfully!')'''
            return redirect(url_for('dashboard'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only letters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    return render_template('register.html', msg=msg)

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/upload')
def upload():
    if 'loggedin' in session:
        return render_template('upload.html')
    return redirect(url_for('login'))

@app.route('/detect')
def detect():
    '''if 'loggedin' in session:
        return render_template('detect.html')
    return redirect(url_for('login'))'''
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    letters = [chr(i) for i in range(65, 91)]  # A-Z
    return render_template('detect.html', letters=letters)

@app.route('/capture/<letter>', methods=['POST'])
def capture(letter):
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    # Run the capture function for the chosen letter
    try:
        capture_images_for_letter(letter)
        return f"Image capture for letter '{letter}' completed! <br><a href='/detect'>Back to detection page</a>"
    except Exception as e:
        return f"Error during capture: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)

'''previous index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='style.css') }}">
    <title>Dashboard</title>
</head>
<body>

    <div class="header">
        <h1 class="word">Welcome, {{ session.username }}!</h1>
    </div>

    <div class="border">
        <p class="word">You are now logged in.</p>
        <a class="btn" href="{{ url_for('logout') }}">Logout</a>
    </div>

</body>
</html>'''