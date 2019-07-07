from flask import Flask, render_template, url_for, flash, redirect, request,session
from flask_sqlalchemy import SQLAlchemy
import datetime
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.secret_key = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Wallet_data.db'

app.config['SQLALCHEMY_BINDS'] = { 'exp': 'sqlite:///Exp_data.db'    }
db = SQLAlchemy(app)

user_name=None
balance=0


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password = db.Column(db.Text,nullable=False)
    balance = db.Column(db.Float)

    def __repr__(self):
        return '<User %r>' % self.username

class Exp(db.Model):
    __bind_key__ = 'exp'

    id = db.Column(db.Integer)
    amount = db.Column(db.Float)
    title = db.Column(db.Text)
    desc = db.Column(db.Text)
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow,primary_key=True)

    def __repr__(self):
        return '<title %r>' % self.title
@app.route("/")
@app.route("/welcome",methods=['GET', 'POST'])
def welcome():
    return redirect(url_for('login'))
    return render_template('welcome.html')

@app.route("/logout",methods=['GET','POST'])

def logout():

    session.pop('id',None)
    session.pop('name',None)
    session.pop('username',None)
    session.pop('balance',None)
    session.pop('_flashes',None)
    flash("Log out successfull")
    return redirect(url_for('welcome'))

    return render_template('logout.html')

@app.route("/delete",methods=['GET','POST'])

def delete():
     error=None
     total=0
     session.pop('_flashes',None)
     if request.method == 'POST':
        for exp in Exp.query.all():
            if exp.id == int(session['id']) and exp.title == request.form['title']:
                db.session.delete(exp)
                db.session.commit()
                flash("Deleted Expense: " + exp.title)
                return redirect(url_for('home'))
        error="Invalid title"
        return render_template('delete.html',error=error)
     return render_template('delete.html',error=error)

@app.route("/view",methods=['GET','POST'])

def view():

    msg="No prior expenses"
    total=0
    session.pop('_flashes',None)
    for exp in Exp.query.all():
        if exp.id == int(session['id']):
            msg="DESCRIPTION: " + exp.title + "{ " + exp.desc + " } AMOUNT: " + str(exp.amount)
            msg = msg + "       Time of last edit: " + str(exp.time)
            total+=float(exp.amount)
            flash(msg)
    flash("Total Amount spent: Rs " + str(total))
    flash("Total Balance: Rs " + str(User.query.filter_by(id=int(session['id'])).first().balance))
    return render_template('view.html')

@app.route("/login",methods=['GET', 'POST'])
def login():
    error=None
    msg=None
    val=0
    if request.method == 'POST':
        passw=request.form['password']

        for user in User.query.all():

                if user.username == request.form['username'] and sha256_crypt.verify(passw,user.password)==True:
                    session.pop('_flashes',None)
                    session['id']  = user.id
                    session['name'] = user.name
                    session['username'] = user.username
                    session['balance'] = user.balance
                    flash("Welcome "+ user.name)
                    flash("Your balance is: Rs " + str(session['balance']))
                    return redirect(url_for('home'))


        error="Invalid credentials"
        return render_template('login.html',error=error)

    return render_template('login.html',error=error)


@app.route("/register",methods = ['GET','POST'])    
def register():
    error = None
    msg = None

    if request.method == 'POST':

        if request.form['password'] != request.form['cpassword']:
            error = "Passwords not matching"
            return render_template('register.html',error=error)
        else:
            for user in User.query.all():
                if user.username == request.form['username']:
                    error = "Username already exists"
                    return render_template('register.html',error=error)
            encrypt_pass = sha256_crypt.encrypt(request.form['password'])
            new_user = User(username=request.form['username'],name=request.form['name'],password=encrypt_pass,balance=request.form['balance'])
            db.session.add(new_user)
            db.session.commit();
            return redirect(url_for('login'))
    else:
        return render_template('register.html',error=error)


@app.route("/home",methods=['GET','POST'])

def home():
    return render_template('home.html')


@app.route("/add",methods=['GET','POST'])

def add():
    error=None
    val=0

    if request.method == 'POST':

            bal = float(session['balance']-float(request.form['amount']))
            User.query.filter_by(username=session['username']).update(dict(balance=bal))
            session['balance']=bal
            db.session.commit()
            new_exp = Exp(id=int(session['id']),amount=request.form['amount'],title=request.form['title'],desc=request.form['desc'],time=datetime.datetime.now())
            db.session.add(new_exp)
            db.session.commit()
            session.pop('_flashes', None)
            flash("Welcome " + session['name'])
            flash(new_exp.title + "{ " + new_exp.desc + " } added successfully")
            flash("Total Balance: Rs " + str(bal))
            return redirect(url_for('home'))

    return render_template('add.html',error=error)




if __name__ == '__main__':
    app.run(debug=True)
