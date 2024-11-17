from flask import Flask, render_template, request, redirect, url_for,session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
 
app=Flask(__name__)
app.secret_key='key1123'

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='chandu123'
app.config['MYSQL_DB']='stores'

mysql=MySQL(app)

def create_signup_table():
    cursor = mysql.connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signup (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            storename VARCHAR(255) NOT NULL       
        )
    ''')
    mysql.connection.commit()
    cursor.close()
def create_products_table():
        cursor = mysql.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
            id INT, foreign key(id) references signup(id) on update cascade on delete cascade,           
            pid INT PRIMARY KEY,
            pname VARCHAR(255) NOT NULL UNIQUE,
            pdesc VARCHAR(255) NOT NULL,
            pprice INT NOT NULL              
            )
        ''')
        mysql.connection.commit()
        cursor.close()

with app.app_context():
    create_signup_table()

@app.route('/')
@app.route('/login',methods=['GET','POST'])
def login() :
    msg=''
    if request.method=='POST' and 'email' in request.form and 'password' in request.form:
        email=request.form['email']
        password=request.form['password']

        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM signup WHERE email=%s and password=%s',(email,password,))
        signup=cursor.fetchone()
        if signup :
            session['loggedin']=True
            session['id']=signup['id']
            session['email']=signup['email']
            session['storename']=signup['storename']
            msg= 'welcome' , session['storename']
            return redirect(url_for('index'))
        else :
            msg='incorrect email or password'
    return render_template('login.html',msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('id',None)
    session.pop('email',None)
    return redirect (url_for('login'))

@app.route('/signup',methods=['GET','POST'])
def signup():
    msg=''
    if request.method=='POST' and 'email'in request.form and 'password' in request.form  and 'storename' in request.form:
        email=request.form ['email']
        password=request.form['password']
        storename=request.form['storename']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM signup WHERE email=%s',(email,))
        signup=cursor.fetchone()
        if signup : 
            msg='account already exists'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg='invalid email'
        elif not re.match(r'[A-Za-z0-9]+', storename):
            msg='store name must contain only words and numbers'
        else :
            cursor.execute('INSERT INTO signup VALUES(NULL,%s,%s,%s)',(email,password,storename,))
            mysql.connection.commit()
            msg='you have logged in ',storename
    elif request.method=='POST':
        msg='please fill'
    return render_template('signup.html',msg=msg)    

@app.route('/index',methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/products',methods=['GET','POST'])
def products():
    with app.app_context():
        create_products_table()

    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT pid, pname, pdesc, pprice FROM products where id=(%s)",)
    products = cursor.fetchall()
    return render_template('products.html', products=products)    

@app.route('/addproduct',methods=['GET','POST'])
def addproduct():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    

if __name__ == '__main__':
    app.run(debug=True)
