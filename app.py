import os
from flask import *
from functools import wraps
from flaskext.mysql import MySQL

SECRET_KEY = 'Chocolate chip cookies'
mysql = MySQL()
app = Flask(__name__) 
# pulls in configurations by looking for UPPERCASE variables 
app.config.from_object(__name__)

app.config['MYSQL_DATABASE_USER'] = 'chintu24x7'
app.config['MYSQL_DATABASE_PASSWORD'] = 'chintooo'
app.config['MYSQL_DATABASE_DB'] = 'c9db'
app.config['MYSQL_DATABASE_HOST'] = 'blawg-db.cm4klal7pqhs.us-east-1.rds.amazonaws.com'
mysql.init_app(app)

conn = mysql.connect()
#connection=mysql.get_db()
cursor = conn.cursor()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods = ['GET', 'POST'])    
def login():
    error = None
    username = request.form['username']
    password = request.form['password']
    
    cursor.execute("SELECT * from User where Username='" + username + "' and Password='" + password + "'")
    data = cursor.fetchone()
    if data is None:
         error = "Wrong username or password"
         return render_template("index.html", error=error)
    else:
         session['logged_in'] = True
         session['username'] = username
         return redirect(url_for("userhome"))

@app.route("/register", methods=['POST'])
def register():
    message = None
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    cursor.execute("SELECT * from User where Username='" + username + "' ")
    data = cursor.fetchone()
    if data is None:
         cursor.execute("INSERT into User values('','" + username + "','" + email + "','" + password + "')")
         conn.commit()
         temp = username + "_blogs"
         cursor.execute("CREATE TABLE "+temp+"(blogId INT NOT NULL AUTO_INCREMENT, title VARCHAR(40) NOT NULL, blogText TEXT, PRIMARY KEY(blogId))")
         conn.commit()
         session['logged_in'] = True
         session['username'] = username
         return redirect(url_for('userhome'))
         
    else:
         message = "Username unavailable. Choose another."
         return render_template("index.html", message=message)
    
def login_required(test):
        @wraps(test)
        def wrap(*args, **kwargs):
            if 'logged_in' in session:
                return test(*args, **kwargs)
            else:
                return redirect(url_for('login'))
        return wrap
    
@app.route("/userhome")    
@login_required
def userhome():
    session['blogInfo']=[]
    temp = session['username'] + "_blogs" #temp is blogtable name
    cursor.execute("SELECT blogId, title from "+temp+" ")
    while True:
        row = cursor.fetchone()
        if row == None:
            break
        session['blogInfo'].append(row)
    leng=len(session['blogInfo'])
    return render_template("userhome.html", username=session['username'], info=session['blogInfo'], leng=leng)
 
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('blogId', None)
    return redirect(url_for('index'))

@app.route("/userhome/new", methods=['GET', 'POST'])
@login_required
def new():
    if request.method=='GET':
        return render_template("new.html",username=session['username'])
    else:
        temp = session['username'] + "_blogs"
        cursor.execute("INSERT into "+temp+" values('', '" + request.form['title'] + "','" + request.form['blogText'] + "')")
        conn.commit()
        return redirect(url_for("userhome"))
        
        
@app.route("/userhome/<blogId>", methods=['GET','POST'])
@login_required
def edit(blogId):
    temp = session['username'] + "_blogs"
    if request.method=='POST':
        cursor.execute("UPDATE "+temp+" SET title='"+request.form['title']+"', blogText='"+request.form['blogText']+"' WHERE blogId="+blogId+"")
        return redirect(url_for("userhome"))
    else:
        cursor.execute("SELECT * from "+temp+" where blogId='" + blogId + "' ")
        blogTuple= cursor.fetchone()
        return render_template("blogEdit.html", blogTuple=blogTuple, username=session['username'])

@app.route("/help")
def hellp():
	return render_template("help.html")
    
app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))