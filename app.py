from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_login import LoginManager, login_user, UserMixin

app = Flask(__name__)

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
    return render_template('index.html')


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f'username: {username}, password: {password}')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = "INSERT INTO login_info (userName, password) Values (%s, %s)"
        try:
            cursor.execute('ALTER TABLE login_info AUTO_INCREMENT = 1')
            cursor.execute(query, (username, password))
            mysql.connection.commit()
            cursor.close()
            print('Signup successful!')
            return render_template('logged.html')
        except MySQLdb.IntegrityError as e:
            mysql.connection.rollback()
            msg = 'Username already exists! Try Login'
            print(msg, e)
    return render_template('signup.html', msg=msg)

@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
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
            return render_template('logged.html')
        else:
            msg = 'Invalid credentials. Please try again.'
    return render_template('index.html', msg=msg)

@app.route('/logged', methods=['POST'])
def logged():
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
