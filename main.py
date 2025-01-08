from flask import Flask, render_template, request, redirect, url_for,session

from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
 
app=Flask(__name__)
app.secret_key='key1123'
app.config['MYSQL_HOST']='munagalachandu.mysql.pythonanywhere-services.com'
app.config['MYSQL_USER']='munagalachandu'
app.config['MYSQL_PASSWORD']='python123'
app.config['MYSQL_DB']='munagalachandu$stores'

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
        id INT, 
        FOREIGN KEY(id) REFERENCES signup(id) ON UPDATE CASCADE ON DELETE CASCADE,
        pid INT PRIMARY KEY,
        pname VARCHAR(255) NOT NULL,
        pdesc TEXT NOT NULL,
        pprice INT NOT NULL
        )

        ''')
        mysql.connection.commit()
        cursor.close()
        

def create_orders_table():
        cursor = mysql.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
        id INT, 
        FOREIGN KEY(id) REFERENCES signup(id) ON UPDATE CASCADE ON DELETE CASCADE,
        oid INT PRIMARY KEY,
        cname VARCHAR(255) NOT NULL,
        cemail VARCHAR(255) NOT NULL,               
        odate DATE NOT NULL,
        status VARCHAR(255) NOT NULL
                    
        )

        ''')
        mysql.connection.commit()
        cursor.close()



def create_cust_orders_table():
        cursor = mysql.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cust_orders (
        id INT, 
        FOREIGN KEY(id) REFERENCES signup(id) ON UPDATE CASCADE ON DELETE CASCADE,
        oid INT,
        pid INT,
        PRIMARY KEY(pid,oid),            
        FOREIGN KEY(oid) REFERENCES orders(oid) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY(pid) REFERENCES products(pid) ON UPDATE CASCADE ON DELETE CASCADE,                                                                           
        p_qty INT NOT NULL
        )

        ''')
        mysql.connection.commit()
        cursor.close()

        
with app.app_context():
    create_signup_table()
with app.app_context():
        create_products_table()    
with app.app_context():
    create_orders_table()
with app.app_context():
    create_cust_orders_table()        

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
            msg= 'welcome'+session['storename']
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
            cursor.execute('INSERT INTO signup (email, password, storename) VALUES (%s, %s, %s)', (email, password, storename))
            mysql.connection.commit()
            msg = f'Account created successfully. Please log in with your email: {email}'
            return redirect(url_for('login'))  # Redirect to login after successful signup
    elif request.method == 'POST':
        msg = 'Please fill in all fields'
    return render_template('signup.html', msg=msg)   

@app.route('/index',methods=['GET','POST'])
def index():
    return render_template('index.html')


@app.route('/profile',methods=['GET','POST'])
def profile():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''select s.storename, count(o.oid) as o_c, count(p.pid) as p_c 
                   from signup s
                    join orders o on s.id=o.id 
                   join products p on p.id=s.id 
                   where s.id=(%s)
                   group by s.storename''',(session['id'],))
    store=cursor.fetchone()
    return render_template('profile.html',store=store)

@app.route('/products',methods=['GET','POST'])
def products():
    
    
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT pid, pname, pdesc, pprice FROM products where id=(%s)",(session['id'],))
    products = cursor.fetchall()
    return render_template('products.html', products=products)    

@app.route('/addproduct',methods=['GET','POST'])
def addproduct():
    msg=''
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method=='POST' and  'pid'in request.form and 'pname' in request.form  and 'pdesc' in request.form and 'pprice' in request.form:
        pid=request.form ['pid']
        pname=request.form['pname']
        pdesc=request.form['pdesc']
        pprice=request.form['pprice']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM products WHERE pid=%s',(pid,))
        products=cursor.fetchone()
        if products : 
            msg='Product ID already exists'
        elif not re.match(r'[0-9]+', pprice):
            msg='Price must contain only numbers'
        else :
            cursor.execute('INSERT INTO products VALUES(%s,%s,%s,%s,%s)',(session['id'],pid,pname,pdesc,pprice,))
            mysql.connection.commit()
            msg='Product added successfully'
            return redirect(url_for('products'))
    elif request.method=='POST':
        msg='Please fill the form'

    return render_template('addproduct.html',msg=msg)   

@app.route('/editproduct/<int:pid>', methods=['GET', 'POST'])
def editproduct(pid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST' and 'pname' in request.form and 'pdesc' in request.form and 'pprice' in request.form:
        pname = request.form['pname']
        pdesc = request.form['pdesc']
        pprice = request.form['pprice']

        cursor.execute('SELECT * FROM products WHERE pid=%s', (pid,))
        product = cursor.fetchone()

        if product:
            cursor.execute('UPDATE products SET pname=%s, pdesc=%s, pprice=%s WHERE pid=%s AND id=%s',
                           (pname, pdesc, pprice, pid, session['id']))
            mysql.connection.commit()

        return redirect(url_for('products'))  

    cursor.execute('SELECT * FROM products WHERE pid=%s AND id=%s', (pid, session['id']))
    product = cursor.fetchone()

    if product:
        return render_template('editproduct.html', product=product)  
    else:
        return redirect(url_for('products'))  

@app.route('/deleteproduct/<int:pid>',methods=['GET','POST'])
def deleteproduct(pid):
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM products WHERE pid=%s AND id=%s',(pid,session['id']))
    mysql.connection.commit()
    return redirect(url_for('products'))

@app.route('/orders', methods=['GET', 'POST'])
def orders():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute('''
        SELECT o.oid, o.cname, o.cemail, o.odate, o.status, co.p_qty, p.pname
        FROM  orders o
        JOIN cust_orders co ON o.oid = co.oid
        JOIN products p ON co.pid = p.pid
        WHERE o.id = %s
        ORDER BY o.oid, p.pname;
    ''', (session['id'],))

    orders_data = cursor.fetchall()

    return render_template('orders.html', orders_data=orders_data)
   

@app.route('/addorder', methods=['GET', 'POST'])
def addorder():
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST' and 'oid' in request.form and 'cname' in request.form and 'cemail' in request.form and 'odate' in request.form and 'status' in request.form and 'pids' in request.form:
        oid = request.form['oid']
        cname = request.form['cname']
        odate = request.form['odate']
        cemail = request.form['cemail']
        pids = request.form.getlist('pids')
        status = request.form['status']

        try:
            cursor.execute('''INSERT INTO orders (id,oid, cname, cemail, odate, status) VALUES (%s,%s, %s, %s, %s, %s)''', (session['id'],oid, cname, cemail, odate, status))
            mysql.connection.commit()

            for pid in pids:
                cursor.execute('''INSERT INTO cust_orders (id, oid, pid, p_qty) VALUES (%s, %s, %s, %s)''', (session['id'], oid, pid, 1))
            mysql.connection.commit()

            return redirect(url_for('orders'))

        except Exception as e:
            return redirect(request.url)
 
    cursor.execute("SELECT pid, pname, pprice FROM products WHERE id=%s", (session['id'],))
    products = cursor.fetchall()

    return render_template('addorder.html', msg=msg, products=products)
 

@app.route('/editorder/<int:oid>', methods=['GET', 'POST'])
def editorder(oid):
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST' and 'cname' in request.form and 'cemail' in request.form and 'odate' in request.form and 'status' in request.form and 'pids' in request.form:
        cname = request.form['cname']
        odate = request.form['odate']
        cemail = request.form['cemail']
        pids = request.form.getlist('pids')
        status = request.form['status']

        try:
            # Update order details
            cursor.execute(''' 
                UPDATE orders 
                SET cname=%s, cemail=%s, odate=%s, status=%s 
                WHERE oid=%s AND id=%s
            ''', (cname, cemail, odate, status, oid, session['id']))
            mysql.connection.commit()

            # Update customer order details
            for pid in pids:
                cursor.execute(''' 
                    UPDATE cust_orders 
                    SET pid=%s, p_qty=%s 
                    WHERE oid=%s AND id=%s
                ''', (pid, 1, oid, session['id']))
            mysql.connection.commit()

            return redirect(url_for('orders'))  # Redirect to orders page

        except Exception as e:
            print(f"Error: {e}")
            return redirect(request.url)  # Redirect back if there's an error
    # Fetch the order details to display in the form
    cursor.execute('''
        SELECT o.oid, o.cname, o.cemail, o.odate, o.status, co.p_qty, p.pname 
        FROM orders o 
        JOIN cust_orders co ON o.oid = co.oid 
        JOIN products p ON co.pid = p.pid 
        WHERE o.oid = %s AND o.id = %s
    ''', (oid, session['id']))
    order = cursor.fetchone()  # Fetch the order details

    if order:
        return render_template('editorder.html', order=order)  # Pass the order details to the template
    else:
        return redirect(url_for('orders'))  # Redirect if order not found



@app.route('/deleteorder/<int:oid>',methods=['GET','POST'])
def deleteorder(oid):
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM orders WHERE oid=%s AND id=%s',(oid,session['id']))
    mysql.connection.commit()
    return redirect(url_for('orders'))
    

    
if __name__ == '__main__':
    app.run(debug=True)
