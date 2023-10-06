from flask import Flask, render_template, request, session, redirect
from flask_session import Session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_login import LoginManager, login_user, UserMixin
# import smtplib
# import socket


# Configure app
app = Flask(__name__)

# Configure Session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.secret_key = 'noSecret'

# Configure MySQL connection
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '0nik@MySQL'
app.config['MYSQL_DB'] = 'students_info'

mysql = MySQL(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    pass


@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM login_info WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()

    if user_data:
        user = User()
        user.id = user_id
        user.username = user_data['userName']
        user.password = user_data['password']
        return user
    return None


@app.route("/", methods=['GET', 'POST'])
def index():
    print("in '/':", session.get('username'))
    if not session.get("username"):
        return redirect("/login")
    return render_template('logged.html')


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET' and not session.get('username'):
        username = request.form.get('username')
        session['username'] = request.form.get("username")
        print('session:', session['username'])
        password = request.form.get('password')
        print(f'username: {username}, password: {password}')
        if not username or not password:
            msg = 'Please fill both!'
            return render_template('signup.html', msg=msg)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = "INSERT INTO login_info (userName, password) Values (%s, %s)"
        try:
            if username and password:
                cursor.execute('ALTER TABLE login_info AUTO_INCREMENT = 1')
                cursor.execute(query, (username, password))
                mysql.connection.commit()
                cursor.close()
                print('Signup successful!')

                # try:
                #     message = 'You are Registered!'
                #     server = smtplib.SMTP("smtp.gmail.com", 587)
                #     server.starttls()
                #     server.login("alahamora84@gmail.com", '')
                #     server.sendmail("alhamora84@gmail.com", username, message)
                #     print('Mail Sent !')
                #     server.quit()
                # except socket.gaierror as e:
                #     print('Offline Error: %s', e)
                # except ConnectionRefusedError as e:
                #     print('Online Error: %s', e)
                # except smtplib.SMTPNotSupportedError as e:
                #     print('SMTP Not Supported Error: %s', e)
                # except smtplib.SMTPAuthenticationError as e:
                #     print('SMTP Authentication Error: %s', e)

                return redirect('/logged')
        except MySQLdb.IntegrityError as e:
            mysql.connection.rollback()
            msg = 'Username already exists! Try Login'
            print(msg, e)
            return render_template('signup.html', msg=msg)
    return redirect('/logged')


@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and not session.get('username'):
        session['username'] = request.form.get("username")
        print('session:', session['username'])
        username = request.form.get('username')
        password = request.form.get('password')
        print(f'username: {username} | password: {password}')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM login_info WHERE userName = %s AND password = %s", (username, password))
        user_data = cursor.fetchone()
        print('userdata: ', user_data)
        cursor.close()
        if user_data:
            user = User()
            user.id = user_data['Id']
            user.username = user_data['userName']
            login_user(user)
            print("logged")
            return redirect('/logged')
        else:
            msg = 'Invalid credentials. Please try again.'

    return render_template('index.html', msg=msg)


@app.route('/logout', methods=['GET'])
def logout():
    session['username'] = None
    print("you are logged out!")
    return redirect('/')


@app.route('/logged', methods=['GET', 'POST'])
def logged():
    print('logged in with:', session.get('username'))
    return render_template('logged.html')


@app.route('/get_users', methods=['GET', 'POST'])
def get_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM login_info")
    users = cur.fetchall()
    cur.close()
    return render_template('users.html', users=users)


if __name__ == '__main__':
    app.run(debug=True)
