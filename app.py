import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor, StackingRegressor, AdaBoostRegressor
from sklearn.tree import ExtraTreeRegressor, DecisionTreeClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from flask import Flask, request, session, redirect, url_for, render_template, flash
import mysql.connector
import os

# ---------------------------
# Admin credentials (dummy)
# ---------------------------
admin_email = "admin@example.com"
admin_password = "admin123"

# ---------------------------
# Flask app setup
# ---------------------------
app = Flask(__name__)
app.secret_key = "fghhdfgdfgrthrttgdfsadfsaffgd"

# ---------------------------
# Database connection
# ---------------------------
# NOTE: For deployment, consider cloud MySQL or SQLite
<<<<<<< HEAD
db = mysql.connector.connect(
    host='localhost',      # Replace with cloud host if using remote DB
    user="root",
    password="",
    port='3306',
    database='Stress1'
)
cur = db.cursor()
=======


import os
import psycopg2

db_url = os.environ["DATABASE_URL"]

conn = psycopg2.connect(db_url)
cursor = conn.cursor()
>>>>>>> 6d2e7b2c10fd825a55ea74aebedd662cce47cdf5

# ---------------------------
# Paths for CSV and model
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Project folder
CSV_PATH = os.path.join(BASE_DIR, "stress_detection_IT_professionals_dataset.csv")
# model.pkl example (if you have a saved model)
# MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

# ---------------------------
# Routes
# ---------------------------
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/home')
def home():
    return render_template("userhome.html")

# ---------------------------
# Admin login/logout
# ---------------------------
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == admin_email and password == admin_password:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            msg = 'Invalid email or password!'
    return render_template('admin_login.html', msg=msg)

@app.route('/admin_panel')
def admin_panel():
    if not session.get('admin_logged_in'):
        flash('Please log in as admin to access the admin panel.', 'danger')
        return redirect(url_for('admin_login'))
    cur.execute("SELECT * FROM allowed_emails")
    allowed_emails = cur.fetchall()
    cur.execute("SELECT Id, Name, Email FROM user")
    registered_users = cur.fetchall()
    return render_template('admin_panel.html', allowed_emails=allowed_emails, registered_users=registered_users)

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("🚪 Logged out successfully.", "info")
    return redirect(url_for('admin_login'))

# ---------------------------
# Admin add/delete emails/users
# ---------------------------
@app.route('/admin/add_email', methods=['POST'])
def add_email():
    email = request.form['email']
    try:
        cur.execute("INSERT INTO allowed_emails (email) VALUES (%s)", (email,))
        db.commit()
        flash("✅ Email added successfully", "success")
    except:
        db.rollback()
        flash("❌ Failed to add email", "danger")
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_email/<int:id>')
def delete_email(id):
    try:
        cur.execute("DELETE FROM allowed_emails WHERE id=%s", (id,))
        db.commit()
        flash("✅ Allowed email deleted successfully", "success")
    except:
        db.rollback()
        flash("❌ Failed to delete allowed email", "danger")
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_user/<int:id>')
def delete_user(id):
    try:
        cur.execute("DELETE FROM user WHERE Id=%s", (id,))
        db.commit()
        flash("✅ Registered user deleted successfully", "success")
    except:
        db.rollback()
        flash("❌ Failed to delete user", "danger")
    return redirect(url_for('admin_panel'))

# ---------------------------
# User login and registration
# ---------------------------
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=='POST':
        useremail=request.form['useremail']
        userpassword=request.form['userpassword']
        sql="SELECT COUNT(*) FROM user WHERE Email=%s AND Password=%s"
        cur.execute(sql, (useremail, userpassword))
        count = cur.fetchone()[0]
        if count == 0:
            flash("❌ Invalid email or password. Please try again.", "danger")
            return redirect(url_for('login'))
        else:
            cur.execute("SELECT * FROM user WHERE Email=%s AND Password=%s", (useremail, userpassword))
            user = cur.fetchone()
            session['email']=useremail
            session['pno']=str(user[4])
            session['name']=str(user[1])
            return render_template("userhome.html", myname=session['name'])
    return render_template('login.html')

@app.route('/registration', methods=["POST", "GET"])
def registration():
    allowed_domains = ['@techcorp.com', '@itcompany.com', '@cybertech.org', '@datasci.in', '@qaeng.com']
    if request.method == 'POST':
        username = request.form['username']
        useremail = request.form['useremail'].lower()
        userpassword = request.form['userpassword']
        conpassword = request.form['conpassword']
        Age = request.form['Age']
        contact = request.form['contact']
        if not any(useremail.endswith(domain) for domain in allowed_domains):
            flash("❌ Registration allowed only for IT employees.", "danger")
            return redirect("/registration")
        if userpassword != conpassword:
            flash("⚠️ Passwords do not match.", "warning")
            return redirect("/registration")
        cur.execute("SELECT * FROM user WHERE Email=%s", (useremail,))
        data = cur.fetchall()
        if data == []:
            sql = "INSERT INTO user(Name, Email, Password, Age, Mob) VALUES (%s,%s,%s,%s,%s)"
            cur.execute(sql, (username, useremail, userpassword, Age, contact))
            db.commit()
            flash("✅ Registered successfully", "success")
            return redirect("/login")
        else:
            flash("⚠️ User already registered.", "warning")
            return redirect("/registration")
    return render_template('registration.html')

# ---------------------------
# View and preprocess data
# ---------------------------
@app.route('/viewdata', methods=["GET","POST"])
def viewdata():
    dataset = pd.read_csv(CSV_PATH)
    return render_template("viewdata.html", columns=dataset.columns.values, rows=dataset.values.tolist())

@app.route('/preprocess', methods=['GET'])
def preprocess():
    global x, y, x_train, x_test, y_train, y_test, df
    df = pd.read_csv(CSV_PATH)
    x = df.drop('Stress_Level', axis=1)
    y = df['Stress_Level']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    return render_template('preprocess.html', msg='✅ Data preprocessed automatically using 30% test split.')

# ---------------------------
# Model selection and prediction
# ---------------------------
@app.route('/model', methods=["POST", "GET"])
def model_route():
    global x_train, y_train, x_test, y_test
    if 'x_train' not in globals():
        return render_template("model.html", msg="⚠️ Please run Preprocess first!")
    if request.method == "POST":
        s = int(request.form['algo'])
        if s == 1:
            rf = RandomForestRegressor()
            rf.fit(x_train, y_train)
            y_pred = rf.predict(x_test)
            score = r2_score(y_pred, y_test)*100
            return render_template("model.html", msg=f"RandomForestRegressor Accuracy: {score:.2f}%")
        # Add other algorithms here as in your original code
    return render_template("model.html")

@app.route('/prediction', methods=["POST","GET"])
def prediction():
    if request.method == "POST":
        # Example: simplified for deployment
        try:
            f1 = float(request.form['Heart_Rate'])
            f2 = float(request.form['Skin_Conductivity'])
            f3 = float(request.form['Hours_Worked'])
            f4 = float(request.form['Emails_Sent'])
            f5 = float(request.form['Meetings_Attended'])
        except:
            return render_template("prediction.html", msg="⚠️ Invalid input.")
        model = RandomForestRegressor()
        model.fit(x_train, y_train)
        result = model.predict([[f1,f2,f3,f4,f5]])
        msg = f"Stress level prediction: {result[0]:.2f}%"
        return render_template("prediction.html", msg=msg)
    return render_template("prediction.html")

# ---------------------------
# Dashboard
# ---------------------------
@app.route('/dashboard')
def dashboard():
    email = session.get('email')
    cur.execute("SELECT date, prediction FROM stress_prediction WHERE email=%s ORDER BY date", (email,))
    data = cur.fetchall()
    dates = [str(row[0]) for row in data]
    stress_levels = [row[1] for row in data]
    return render_template('dashboard.html', dates=dates, stress_levels=stress_levels)

# ---------------------------
# Run app (deployment-ready)
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Cloud port
    app.run(host="0.0.0.0", port=port)
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor, StackingRegressor, AdaBoostRegressor
from sklearn.tree import ExtraTreeRegressor, DecisionTreeClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from flask import Flask, request, session, redirect, url_for, render_template, flash
import mysql.connector
import os

# ---------------------------
# Admin credentials (dummy)
# ---------------------------
admin_email = "admin@example.com"
admin_password = "admin123"

# ---------------------------
# Flask app setup
# ---------------------------
app = Flask(__name__)
app.secret_key = "fghhdfgdfgrthrttgdfsadfsaffgd"

# ---------------------------
# Database connection
# ---------------------------
# NOTE: For deployment, consider cloud MySQL or SQLite
db = mysql.connector.connect(
    host='localhost',      # Replace with cloud host if using remote DB
    user="root",
    password="",
    port='3306',
    database='Stress1'
)
cur = db.cursor()

# ---------------------------
# Paths for CSV and model
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Project folder
CSV_PATH = os.path.join(BASE_DIR, "stress_detection_IT_professionals_dataset.csv")
# model.pkl example (if you have a saved model)
# MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

# ---------------------------
# Routes
# ---------------------------
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/home')
def home():
    return render_template("userhome.html")

# ---------------------------
# Admin login/logout
# ---------------------------
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == admin_email and password == admin_password:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            msg = 'Invalid email or password!'
    return render_template('admin_login.html', msg=msg)

@app.route('/admin_panel')
def admin_panel():
    if not session.get('admin_logged_in'):
        flash('Please log in as admin to access the admin panel.', 'danger')
        return redirect(url_for('admin_login'))
    cur.execute("SELECT * FROM allowed_emails")
    allowed_emails = cur.fetchall()
    cur.execute("SELECT Id, Name, Email FROM user")
    registered_users = cur.fetchall()
    return render_template('admin_panel.html', allowed_emails=allowed_emails, registered_users=registered_users)

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("🚪 Logged out successfully.", "info")
    return redirect(url_for('admin_login'))

# ---------------------------
# Admin add/delete emails/users
# ---------------------------
@app.route('/admin/add_email', methods=['POST'])
def add_email():
    email = request.form['email']
    try:
        cur.execute("INSERT INTO allowed_emails (email) VALUES (%s)", (email,))
        db.commit()
        flash("✅ Email added successfully", "success")
    except:
        db.rollback()
        flash("❌ Failed to add email", "danger")
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_email/<int:id>')
def delete_email(id):
    try:
        cur.execute("DELETE FROM allowed_emails WHERE id=%s", (id,))
        db.commit()
        flash("✅ Allowed email deleted successfully", "success")
    except:
        db.rollback()
        flash("❌ Failed to delete allowed email", "danger")
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_user/<int:id>')
def delete_user(id):
    try:
        cur.execute("DELETE FROM user WHERE Id=%s", (id,))
        db.commit()
        flash("✅ Registered user deleted successfully", "success")
    except:
        db.rollback()
        flash("❌ Failed to delete user", "danger")
    return redirect(url_for('admin_panel'))

# ---------------------------
# User login and registration
# ---------------------------
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=='POST':
        useremail=request.form['useremail']
        userpassword=request.form['userpassword']
        sql="SELECT COUNT(*) FROM user WHERE Email=%s AND Password=%s"
        cur.execute(sql, (useremail, userpassword))
        count = cur.fetchone()[0]
        if count == 0:
            flash("❌ Invalid email or password. Please try again.", "danger")
            return redirect(url_for('login'))
        else:
            cur.execute("SELECT * FROM user WHERE Email=%s AND Password=%s", (useremail, userpassword))
            user = cur.fetchone()
            session['email']=useremail
            session['pno']=str(user[4])
            session['name']=str(user[1])
            return render_template("userhome.html", myname=session['name'])
    return render_template('login.html')

@app.route('/registration', methods=["POST", "GET"])
def registration():
    allowed_domains = ['@techcorp.com', '@itcompany.com', '@cybertech.org', '@datasci.in', '@qaeng.com']
    if request.method == 'POST':
        username = request.form['username']
        useremail = request.form['useremail'].lower()
        userpassword = request.form['userpassword']
        conpassword = request.form['conpassword']
        Age = request.form['Age']
        contact = request.form['contact']
        if not any(useremail.endswith(domain) for domain in allowed_domains):
            flash("❌ Registration allowed only for IT employees.", "danger")
            return redirect("/registration")
        if userpassword != conpassword:
            flash("⚠️ Passwords do not match.", "warning")
            return redirect("/registration")
        cur.execute("SELECT * FROM user WHERE Email=%s", (useremail,))
        data = cur.fetchall()
        if data == []:
            sql = "INSERT INTO user(Name, Email, Password, Age, Mob) VALUES (%s,%s,%s,%s,%s)"
            cur.execute(sql, (username, useremail, userpassword, Age, contact))
            db.commit()
            flash("✅ Registered successfully", "success")
            return redirect("/login")
        else:
            flash("⚠️ User already registered.", "warning")
            return redirect("/registration")
    return render_template('registration.html')

# ---------------------------
# View and preprocess data
# ---------------------------
@app.route('/viewdata', methods=["GET","POST"])
def viewdata():
    dataset = pd.read_csv(CSV_PATH)
    return render_template("viewdata.html", columns=dataset.columns.values, rows=dataset.values.tolist())

@app.route('/preprocess', methods=['GET'])
def preprocess():
    global x, y, x_train, x_test, y_train, y_test, df
    df = pd.read_csv(CSV_PATH)
    x = df.drop('Stress_Level', axis=1)
    y = df['Stress_Level']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    return render_template('preprocess.html', msg='✅ Data preprocessed automatically using 30% test split.')

# ---------------------------
# Model selection and prediction
# ---------------------------
@app.route('/model', methods=["POST", "GET"])
def model_route():
    global x_train, y_train, x_test, y_test
    if 'x_train' not in globals():
        return render_template("model.html", msg="⚠️ Please run Preprocess first!")
    if request.method == "POST":
        s = int(request.form['algo'])
        if s == 1:
            rf = RandomForestRegressor()
            rf.fit(x_train, y_train)
            y_pred = rf.predict(x_test)
            score = r2_score(y_pred, y_test)*100
            return render_template("model.html", msg=f"RandomForestRegressor Accuracy: {score:.2f}%")
        # Add other algorithms here as in your original code
    return render_template("model.html")

@app.route('/prediction', methods=["POST","GET"])
def prediction():
    if request.method == "POST":
        # Example: simplified for deployment
        try:
            f1 = float(request.form['Heart_Rate'])
            f2 = float(request.form['Skin_Conductivity'])
            f3 = float(request.form['Hours_Worked'])
            f4 = float(request.form['Emails_Sent'])
            f5 = float(request.form['Meetings_Attended'])
        except:
            return render_template("prediction.html", msg="⚠️ Invalid input.")
        model = RandomForestRegressor()
        model.fit(x_train, y_train)
        result = model.predict([[f1,f2,f3,f4,f5]])
        msg = f"Stress level prediction: {result[0]:.2f}%"
        return render_template("prediction.html", msg=msg)
    return render_template("prediction.html")

# ---------------------------
# Dashboard
# ---------------------------
@app.route('/dashboard')
def dashboard():
    email = session.get('email')
    cur.execute("SELECT date, prediction FROM stress_prediction WHERE email=%s ORDER BY date", (email,))
    data = cur.fetchall()
    dates = [str(row[0]) for row in data]
    stress_levels = [row[1] for row in data]
    return render_template('dashboard.html', dates=dates, stress_levels=stress_levels)

# ---------------------------
# Run app (deployment-ready)
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Cloud port
    app.run(host="0.0.0.0", port=port)
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor, StackingRegressor, AdaBoostRegressor
from sklearn.tree import ExtraTreeRegressor, DecisionTreeClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from flask import Flask, request, session, redirect, url_for, render_template, flash
import mysql.connector
import os

# ---------------------------
# Admin credentials (dummy)
# ---------------------------
admin_email = "admin@example.com"
admin_password = "admin123"

# ---------------------------
# Flask app setup
# ---------------------------
app = Flask(__name__)
app.secret_key = "fghhdfgdfgrthrttgdfsadfsaffgd"

# ---------------------------
# Database connection
# ---------------------------
# NOTE: For deployment, consider cloud MySQL or SQLite
db = mysql.connector.connect(
    host='localhost',      # Replace with cloud host if using remote DB
    user="root",
    password="",
    port='3306',
    database='Stress1'
)
cur = db.cursor()

# ---------------------------
# Paths for CSV and model
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Project folder
CSV_PATH = os.path.join(BASE_DIR, "stress_detection_IT_professionals_dataset.csv")
# model.pkl example (if you have a saved model)
# MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

# ---------------------------
# Routes
# ---------------------------
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/home')
def home():
    return render_template("userhome.html")

# ---------------------------
# Admin login/logout
# ---------------------------
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == admin_email and password == admin_password:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            msg = 'Invalid email or password!'
    return render_template('admin_login.html', msg=msg)

@app.route('/admin_panel')
def admin_panel():
    if not session.get('admin_logged_in'):
        flash('Please log in as admin to access the admin panel.', 'danger')
        return redirect(url_for('admin_login'))
    cur.execute("SELECT * FROM allowed_emails")
    allowed_emails = cur.fetchall()
    cur.execute("SELECT Id, Name, Email FROM user")
    registered_users = cur.fetchall()
    return render_template('admin_panel.html', allowed_emails=allowed_emails, registered_users=registered_users)

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("🚪 Logged out successfully.", "info")
    return redirect(url_for('admin_login'))

# ---------------------------
# Admin add/delete emails/users
# ---------------------------
@app.route('/admin/add_email', methods=['POST'])
def add_email():
    email = request.form['email']
    try:
        cur.execute("INSERT INTO allowed_emails (email) VALUES (%s)", (email,))
        db.commit()
        flash("✅ Email added successfully", "success")
    except:
        db.rollback()
        flash("❌ Failed to add email", "danger")
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_email/<int:id>')
def delete_email(id):
    try:
        cur.execute("DELETE FROM allowed_emails WHERE id=%s", (id,))
        db.commit()
        flash("✅ Allowed email deleted successfully", "success")
    except:
        db.rollback()
        flash("❌ Failed to delete allowed email", "danger")
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_user/<int:id>')
def delete_user(id):
    try:
        cur.execute("DELETE FROM user WHERE Id=%s", (id,))
        db.commit()
        flash("✅ Registered user deleted successfully", "success")
    except:
        db.rollback()
        flash("❌ Failed to delete user", "danger")
    return redirect(url_for('admin_panel'))

# ---------------------------
# User login and registration
# ---------------------------
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=='POST':
        useremail=request.form['useremail']
        userpassword=request.form['userpassword']
        sql="SELECT COUNT(*) FROM user WHERE Email=%s AND Password=%s"
        cur.execute(sql, (useremail, userpassword))
        count = cur.fetchone()[0]
        if count == 0:
            flash("❌ Invalid email or password. Please try again.", "danger")
            return redirect(url_for('login'))
        else:
            cur.execute("SELECT * FROM user WHERE Email=%s AND Password=%s", (useremail, userpassword))
            user = cur.fetchone()
            session['email']=useremail
            session['pno']=str(user[4])
            session['name']=str(user[1])
            return render_template("userhome.html", myname=session['name'])
    return render_template('login.html')

@app.route('/registration', methods=["POST", "GET"])
def registration():
    allowed_domains = ['@techcorp.com', '@itcompany.com', '@cybertech.org', '@datasci.in', '@qaeng.com']
    if request.method == 'POST':
        username = request.form['username']
        useremail = request.form['useremail'].lower()
        userpassword = request.form['userpassword']
        conpassword = request.form['conpassword']
        Age = request.form['Age']
        contact = request.form['contact']
        if not any(useremail.endswith(domain) for domain in allowed_domains):
            flash("❌ Registration allowed only for IT employees.", "danger")
            return redirect("/registration")
        if userpassword != conpassword:
            flash("⚠️ Passwords do not match.", "warning")
            return redirect("/registration")
        cur.execute("SELECT * FROM user WHERE Email=%s", (useremail,))
        data = cur.fetchall()
        if data == []:
            sql = "INSERT INTO user(Name, Email, Password, Age, Mob) VALUES (%s,%s,%s,%s,%s)"
            cur.execute(sql, (username, useremail, userpassword, Age, contact))
            db.commit()
            flash("✅ Registered successfully", "success")
            return redirect("/login")
        else:
            flash("⚠️ User already registered.", "warning")
            return redirect("/registration")
    return render_template('registration.html')

# ---------------------------
# View and preprocess data
# ---------------------------
@app.route('/viewdata', methods=["GET","POST"])
def viewdata():
    dataset = pd.read_csv(CSV_PATH)
    return render_template("viewdata.html", columns=dataset.columns.values, rows=dataset.values.tolist())

@app.route('/preprocess', methods=['GET'])
def preprocess():
    global x, y, x_train, x_test, y_train, y_test, df
    df = pd.read_csv(CSV_PATH)
    x = df.drop('Stress_Level', axis=1)
    y = df['Stress_Level']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    return render_template('preprocess.html', msg='✅ Data preprocessed automatically using 30% test split.')

# ---------------------------
# Model selection and prediction
# ---------------------------
@app.route('/model', methods=["POST", "GET"])
def model_route():
    global x_train, y_train, x_test, y_test
    if 'x_train' not in globals():
        return render_template("model.html", msg="⚠️ Please run Preprocess first!")
    if request.method == "POST":
        s = int(request.form['algo'])
        if s == 1:
            rf = RandomForestRegressor()
            rf.fit(x_train, y_train)
            y_pred = rf.predict(x_test)
            score = r2_score(y_pred, y_test)*100
            return render_template("model.html", msg=f"RandomForestRegressor Accuracy: {score:.2f}%")
        # Add other algorithms here as in your original code
    return render_template("model.html")

@app.route('/prediction', methods=["POST","GET"])
def prediction():
    if request.method == "POST":
        # Example: simplified for deployment
        try:
            f1 = float(request.form['Heart_Rate'])
            f2 = float(request.form['Skin_Conductivity'])
            f3 = float(request.form['Hours_Worked'])
            f4 = float(request.form['Emails_Sent'])
            f5 = float(request.form['Meetings_Attended'])
        except:
            return render_template("prediction.html", msg="⚠️ Invalid input.")
        model = RandomForestRegressor()
        model.fit(x_train, y_train)
        result = model.predict([[f1,f2,f3,f4,f5]])
        msg = f"Stress level prediction: {result[0]:.2f}%"
        return render_template("prediction.html", msg=msg)
    return render_template("prediction.html")

# ---------------------------
# Dashboard
# ---------------------------
@app.route('/dashboard')
def dashboard():
    email = session.get('email')
    cur.execute("SELECT date, prediction FROM stress_prediction WHERE email=%s ORDER BY date", (email,))
    data = cur.fetchall()
    dates = [str(row[0]) for row in data]
    stress_levels = [row[1] for row in data]
    return render_template('dashboard.html', dates=dates, stress_levels=stress_levels)

# ---------------------------
# Run app (deployment-ready)
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Cloud port
    app.run(host="0.0.0.0", port=port)
<<<<<<< HEAD
    
=======
    
>>>>>>> 6d2e7b2c10fd825a55ea74aebedd662cce47cdf5
