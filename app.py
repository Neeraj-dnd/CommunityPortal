from flask import Flask, render_template, request, session, redirect, flash, send_from_directory
from flask_session import Session
import mysql.connector
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_login import LoginManager, login_user, UserMixin
import bcrypt

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

# Configure the MySQL database connection for registered students
db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "0nik@MySQL",
    "database": "app_test",
}

Mysql = MySQL(app)

login_manager = LoginManager()
login_manager.init_app(app)

cnx = mysql.connector.connect(**db_config)
Cursor = cnx.cursor()


class User(UserMixin):
    pass


@login_manager.user_loader
def load_user(user_id):
    print('\n-> Inside Load_user func')
    cursor = Mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM login_info WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    print('> user_data:', user_data)

    if user_data:
        user = User()
        user.id = user_id
        user.username = user_data['userName']
        user.password = user_data['password']
        return user
    return None


@app.route("/", methods=['GET', 'POST'])
def index():
    print("\n-> in '/':", session.get('username'))
    if not session.get("username"):
        print('\n-> Session not found')
        return render_template('index.html')
    print('\n-> outside if')
    return redirect('/logged')


@app.route("/signup_page", methods=['GET'])
def signup_page():
    print('\ninside signup_page')
    if request.method == 'GET' and not session.get('username'):
        print('rendering signup temp')
        return render_template('signup.html')
    return redirect("/signup")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    print('\n-> Inside /signup')
    msg = ''

    if request.method == 'POST' and not session.get('username'):
        username = request.form.get('username')
        password = request.form.get('password')

        cursor = Mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check if the username already exists
        cursor.execute("SELECT * FROM login_info WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            msg = 'Username already exists. Please choose a different username.'
        else:
            # Hash the password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Insert the user into the database
            cursor.execute("INSERT INTO login_info (userName, password) VALUES (%s, %s)", (username, hashed_password))
            Mysql.connection.commit()
            cursor.close()
            print('Signup successful!')
            return redirect('/logged')

    return render_template('signup.html', msg=msg)


@app.route("/login", methods=['GET', 'POST'])
def login():
    print('\n-> Inside /login')
    msg = ''

    if request.method == 'POST' and not session.get('username'):
        username = request.form.get('username')
        password = request.form.get('password')
        print(f'username: {username} | password: {password}')

        cursor = Mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM login_info WHERE userName = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()
        print("userdata:", user_data)

        if user_data:
            stored_password = user_data['password']

            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                user = User()
                user.id = user_data['Id']
                user.username = user_data['userName']
                login_user(user)
                session['username'] = request.form.get("username")
                return redirect('/logged')
            else:
                msg = 'Invalid password. Please try again.'

        else:
            msg = 'Username not found. Please try again.'

    return render_template('index.html', msg=msg)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['username'] = None
    print("you are logged out!")
    return redirect('/')


@app.route('/logged', methods=['GET', 'POST'])
def logged():
    print('\n-> Inside /logged')
    if not session.get("username"):
        print('\n-> inside if')
        return redirect("/login")
    print('logged in with:', session.get('username'))

    cursor = Mysql.connection.cursor()
    cursor.execute("SELECT * FROM user_posts")
    posts = reversed(cursor.fetchall())
    cursor.close()
    return render_template('home.html', posts=posts)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    print('\n-> Inside /profile')
    if not session.get("username"):
        print('\n-> inside if')
        return redirect("/login")
    print('profile of:', session.get('username'))
    return render_template('user.html')


@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    print('\n-> inside add post')
    if not session.get("username"):
        print('\n-> inside if')
        return redirect("/login")
    print(session.get('username'), 'is adding post.')
    return render_template('add_post.html')


@app.route('/upload_post', methods=['GET', 'POST'])
def upload_post():
    print('\n-> uploading post')
    if 'username' not in session:
        return redirect("/login")
    print(session.get('username'), 'is uploading post.')

    if request.method == 'POST':
        print("inside uploading post")
        cursor = Mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM login_info WHERE userName = %s", (session.get('username'),))
        user_data = cursor.fetchone()
        cursor.close()

        userId = user_data['Id']
        title = request.form['title']
        post_description = request.form['post_description']
        image = request.files['image_name']
        print('\nuserId: ', userId,
              '\ntitle: ', title,
              '\npost_description: ', post_description)

        # Save the uploaded image to a specific directory, e.g., 'uploads'
        image.save('uploads/' + str(image.filename))
        image_name = image.filename

        cursor = Mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO user_posts (userId, title, post_description, image_name) VALUES (%s, %s, %s, %s)",
            (userId, title, post_description, image_name)
        )
        Mysql.connection.commit()
        cursor.close()

        flash('Post uploaded successfully', 'success')  # You can use flash messages for user feedback

    return redirect('/logged')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)


@app.route('/get_users', methods=['GET', 'POST'])
def get_users():
    cur = Mysql.connection.cursor()
    cur.execute("SELECT * FROM login_info")
    users = cur.fetchall()
    cur.close()
    return render_template('users.html', users=users)


@app.route('/fill_form', methods=['GET', 'POST'])
def home():
    return render_template('form.html')


@app.route("/form_submit", methods=['GET', 'POST'])
def form_submit():
    msg = ' '
    try:
        if request.method == 'POST':
            print("Inside submit_form funtion...")
            first_name = request.form.get('first_name')
            last_name = request.form['last_name']
            father = request.form['father']
            mother = request.form['mother']
            address = request.form['address']
            state = request.form['state']
            city = request.form['city']
            gender = request.form['gender']
            dob = request.form['dob']
            pincode = request.form['pincode']
            email = request.form['email']
            if not first_name or not last_name or not father or not address or not state:
                if not city or not gender or not dob or not pincode or not email:
                    msg = 'Please fill all info !'
                    print("error:", msg)
            Cursor.execute(
                "INSERT INTO Registered_students (first_name, last_name, father, mother, address, state, city, "
                "gender, dob, pincode, email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (first_name, last_name, father, mother, address, state, city, gender, dob, pincode, email))
            cnx.commit()
            print('Successfully Registered')
            return render_template('user.html')
    finally:
        print('some issue..')

    return render_template("index.html", msg=msg)


@app.route("/students/registered", methods=["GET", "POST"])
def fetch_data():
    print("inside Fetch function")
    if request.method == 'GET':
        print("fetching data...")
        # Execute a SELECT query to fetch data from the database
        Cursor.execute("SELECT * FROM Registered_students")
        data = Cursor.fetchall()
        print(data)
        return render_template('Registered_students.html', Students_data=data)


@app.route("/students/edit/<int:id>", methods=['GET'])
def edit(id):
    print('Editing...')
    # select based on id
    Cursor.execute("SELECT * FROM Registered_students WHERE id=%s", (id,))
    data = Cursor.fetchone()
    return render_template('edit.html', Student_data=data)


@app.route("/students/delete/<int:id>", methods=['GET'])
def delete(id):
    print('Deleting...')
    Cursor.execute("DELETE FROM Registered_students WHERE id=%s", (id,))
    return redirect("/students/registered")


# update
@app.route("/students/updateInfo", methods=['POST'])
def update():
    print('Updating...')
    if request.method == 'POST':
        id = request.form['id']
        print("Inside update_form funtion...")
        first_name = request.form.get('first_name')
        last_name = request.form['last_name']
        father = request.form['father']
        mother = request.form['mother']
        address = request.form['address']
        state = request.form['state']
        city = request.form['city']
        gender = request.form['gender']
        dob = request.form['dob']
        pincode = request.form['pincode']
        email = request.form['email']
        Cursor.execute(
            "UPDATE Registered_students SET first_name=%s, last_name=%s, father=%s, mother=%s, address=%s, state=%s, "
            "city=%s, gender=%s, dob=%s, pincode=%s, email=%s WHERE id=%s",
            (first_name, last_name, father, mother, address, state, city, gender, dob, pincode, email, id))
        cnx.commit()
        print('Successfully Updated Info')
        return redirect("/students/registered")
    return redirect('/students/updateInfo')


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
