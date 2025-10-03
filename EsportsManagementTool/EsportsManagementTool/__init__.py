# This Flask project is set up in the packages format, meaning we can
# separate our application into multiple modules that are then imported
# into __init__.py here

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import bcrypt
app = Flask(__name__)

# Module imports
import EsportsManagementTool.exampleModule

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = '134.210.208.51'
app.config['MYSQL_USER'] = 'tableconfig'
app.config['MYSQL_PASSWORD'] = 'T4b1eCR34TI0ni$FuN*@#'
app.config['MYSQL_DB'] = 'esportsmanagementtool'

app.config['MYSQL_SSL_DISABLED'] = False
app.config['MYSQL_CUSTOM_OPTIONS'] = {
    'ssl_mode': 'REQUIRED'
}

"""
All security settings were developed in part with Claude.ai.
Forcing HTTPS developed in part with Claude.ai.
SSL security and bcrypt set to hash and salt passwords, and to ensure no data
leakage across packet transferring. 
"""
mysql = MySQL(app)

# For production, force HTTPS
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            account = cursor.fetchone()

            if account and bcrypt.checkpw(password.encode('utf-8'), account['password'].encode('utf-8')):
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                return redirect(url_for('profile'))
            else:
                msg = 'Incorrect username/password!'
        finally:
            cursor.close()

    return render_template('login.html', msg=msg)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('Successfully logged out.')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'passwordconfirm' in request.form and 'email' in request.form:

        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        password = request.form['password']
        passwordconfirm = request.form['passwordconfirm']
        email = request.form['email']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            account = cursor.fetchone()

            if account:
                msg = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif password != passwordconfirm:
                msg = 'Passwords do not match!'
            elif not (email.endswith('@stockton.edu') or email.endswith('@go.stockton.edu')):
                msg = 'Email must be a Stockton email address (@stockton.edu or @go.stockton.edu)!'
            elif not username or not password or not email:
                msg = 'Please fill out the form!'
            else:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute(
                    'INSERT INTO users (firstname, lastname, username, password, email) VALUES (%s, %s, %s, %s, %s)',
                    (firstname, lastname, username, hashed_password, email))
                mysql.connection.commit()
                msg = 'You have successfully registered! Welcome to Stockton Esports!'
        finally:
            cursor.close()

    elif request.method == 'POST':
        msg = 'Please fill out the form!'

    return render_template('register.html', msg=msg)


@app.route('/profile')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
            account = cursor.fetchone()
            return render_template('profile.html', account=account)
        finally:
            cursor.close()
    return redirect(url_for('login'))

#App route to get to event registration.
@app.route('/event-register', methods=['GET', 'POST'])
#eventRegister method
def eventRegister():
    msg = ''
    if request.method == 'POST':

        #Receives a user response for all of eventName, eventDate, eventTime, and eventDescription
        eventName = request.form.get('eventName', '').strip()
        eventDate = request.form.get('eventDate', '').strip()
        eventTime = request.form.get('eventTime', '').strip()
        eventDescription = request.form.get('eventDescription', '').strip()

    #Does what needs to be done if the fields are filled out.
        if eventName and eventDate and eventTime and eventDescription:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            try:
                cursor.execute('INSERT INTO events (name, date, time, description) VALUES (%s, %s, %s, %s)', (eventName, eventDate, eventTime, eventDescription))

                #Confirms that the event is registered.
                mysql.connection.commit()
                msg = 'Event Registered!'

            except Exception as e:
                msg = f'Error: {str(e)}'
            finally:
                cursor.close()

        #Prompts user to fill out all fields if they leave any/all blank.
        else:
            msg = 'Please fill out all fields!'

    #Uses the event-register html file to render the page.
    return render_template('event-register.html', msg=msg)

@app.route("/test")
def test():
    return "<p> This is a test </p>"
