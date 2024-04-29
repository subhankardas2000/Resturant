from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange
import sqlite3
from flask import session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure secret key

# Database initialization
conn = sqlite3.connect('database.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        is_admin BOOLEAN NOT NULL DEFAULT 0,
        user_type TEXT NOT NULL DEFAULT 'customer'
    )
''')

conn.execute('''
    CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT NOT NULL,
        price REAL NOT NULL
    )
''')

conn.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        is_online_payment BOOLEAN NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (item_id) REFERENCES menu(id)
    )
''')

conn.execute('''
    CREATE TABLE IF NOT EXISTS user_query(
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT NOT NULL
    )
''')

conn.close()

# Wtforms...
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    user_type = SelectField('User Type', choices=[('customer', 'Customer'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    user_type = SelectField('User Type', choices=[('customer', 'Customer'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')
    
class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
class CustomerLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class OrderForm(FlaskForm):
    item = SelectField('Item', coerce=int)
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    online_payment = BooleanField('Pay Online')
    submit = SubmitField('Place Order')

# app routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            message = request.form['message']

            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO user_query (name, email, message) VALUES (?, ?, ?)", (name, email, message))
                con.commit()

        except Exception as e:
            print(e)
            con.rollback()
            return render_template("404.html")
        return render_template("messagesuccess.html")
    return render_template('contact.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('is_admin', None)
    flash('Logged out successfully', 'success')
    return render_template('logout.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user_type = form.user_type.data

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, is_admin, user_type) VALUES (?, ?, ?, ?)", (username, password, user_type == 'admin', user_type))
        conn.commit()
        conn.close()

        #flash('Sign up successful', 'success')
        return render_template('signupsuccess.html')
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user_type = form.user_type.data

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, is_admin FROM users WHERE username=? AND password=? AND user_type=?", (username, password, user_type))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = username
            session['is_admin'] = (user_type == 'admin')
            flash('Login successful', 'success')
            if user_type == 'admin':
                return redirect(url_for('admintask'))
            else:
                # Pass the OrderForm instance to the customer.html template
                order_form = OrderForm()
                return redirect(url_for('customerorder', form=order_form))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    form = AdminLoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=? AND password=? AND is_admin=1", (username, password))
        admin_id = cursor.fetchone()
        conn.close()

        if admin_id:
            session['user'] = username
            session['is_admin'] = True
            flash('Admin login successful', 'success')
            return redirect(url_for('admintask'))
        else:
            flash('Invalid username or password for admin', 'error')
    return render_template('login.html', form=form)

@app.route('/admintask', methods=['GET', 'POST'])
def admintask():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
                SELECT u.username, m.item, m.price, o.quantity, o.is_online_payment 
                FROM orders o 
                INNER JOIN users u ON o.user_id = u.id
                INNER JOIN menu m ON o.item_id = m.id
            """)
    orders = cursor.fetchall()

            # Fetch menu items with their prices
    cursor.execute("SELECT item, price FROM menu")
    menu_items = cursor.fetchall()

            # Fetch customer messages
    cursor.execute("SELECT * FROM user_query")
    messages = cursor.fetchall()   
    conn.close()
    return render_template('admin.html', orders=orders, menu_items=menu_items,messages=messages)

@app.route('/customer', methods=['GET', 'POST'])
def customer():
    form = CustomerLoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=? AND password=? AND is_admin=0", (username, password))
        admin_id = cursor.fetchone()
        conn.close()

        if admin_id:
            session['user'] = username
            session['is_admin'] = False
            flash('Customer login successful', 'success')
            return redirect(url_for('customerorder', form=form))

@app.route('/customerorder', methods=['GET', 'POST'])
def customerorder():
    form = OrderForm()

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, item FROM menu")
    menu_items = cursor.fetchall()
    conn.close()

    form.item.choices = menu_items
    
    if form.validate_on_submit():
        user_id = 1  # You should get the actual user_id from the session or database
        item_id = form.item.data
        quantity = form.quantity.data
        is_online_payment = form.online_payment.data

        # Calculate total price      
          
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (user_id, item_id, quantity, is_online_payment) VALUES (?, ?, ?, ?)",
                       (user_id, item_id, quantity, is_online_payment))
        conn.commit()
        conn.close()  
        
        flash('Order placed successfully', 'success')
        return render_template('orderconfirm.html', form=form)
    
    #return render_template('customer.html', form=form)


    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT item, price FROM menu")
    menu = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]
    available_seats = 50 - total_orders
    conn.close()
    return render_template('customer.html', form=form, menu=menu, available_seats=available_seats)


@app.route('/orderconfirm')
def orderconfirm():
    # Fetch order details from the database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT item_id, quantity, total_price, is_online_payment FROM orders ORDER BY id DESC LIMIT 1")
    order_data = cursor.fetchone()
    conn.close()

    if order_data:
        # Get item details from the menu table
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT item, price FROM menu WHERE id=?", (order_data[0],))
        item_details = cursor.fetchone()
        conn.close()

        if item_details:
            order = {
                'item': item_details[0],
                'quantity': order_data[1],
                'total_price': order_data[2],
                'is_online_payment': order_data[3]
            }
            return render_template('orderconfirm.html', order=order)
    # If no order found or error occurred, redirect to customerorder page
    return redirect(url_for('customerorder'))

if __name__ == '__main__':
    app.run(debug=True)