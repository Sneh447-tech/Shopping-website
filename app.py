from flask import Flask, render_template, request, redirect, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "secret123"

# HOME
@app.route('/')
def home():
    return render_template("index.html")

# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if not os.path.exists("users.csv"):
            df = pd.DataFrame(columns=["Name","Email","Password"])
            df.to_csv("users.csv", index=False)

        new_user = pd.DataFrame([[name,email,password]],
                                columns=["Name","Email","Password"])
        new_user.to_csv("users.csv", mode='a', header=False, index=False)

        return redirect('/login')

    return render_template("register.html")

# LOGIN
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        users = pd.read_csv("users.csv")

        user = users[(users["Email"] == email) & (users["Password"] == password)]

        if len(user) > 0:
            session['user'] = email
            return redirect('/products')
        else:
            return "Invalid Login ❌"

    return render_template("login.html")

# PRODUCTS
@app.route('/products')
def products():
    if 'user' not in session:
        return redirect('/login')

    df = pd.read_csv("products.csv")
    return render_template("products.html", products=df.to_dict(orient='records'))

# ADD TO CART
@app.route('/add-to-cart/<int:id>')
def add_to_cart(id):
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']

    if str(id) in cart:
        cart[str(id)] += 1
    else:
        cart[str(id)] = 1

    session['cart'] = cart

    return redirect('/cart')

# CART
@app.route('/cart')
def cart():
    if 'user' not in session:
        return redirect('/login')

    cart = session.get('cart', {})
    df = pd.read_csv("products.csv")

    items = []
    total = 0

    for pid, qty in cart.items():
        product = df[df['id'] == int(pid)].iloc[0]

        subtotal = product['price'] * qty
        total += subtotal

        items.append({
            "id": product['id'],
            "name": product['name'],
            "price": product['price'],
            "image": product['image'],
            "qty": qty,
            "subtotal": subtotal
        })

    return render_template("cart.html", items=items, total=total)

# PAYMENT
@app.route('/payment')
def payment():
    return render_template("payment.html")

# SUCCESS
@app.route('/success')
def success():
    return render_template("success.html")

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# RUN
if __name__ == "__main__":
    app.run(debug=True)