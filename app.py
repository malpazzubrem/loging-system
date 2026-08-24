from flask import Flask, render_template,request,session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 
from flask_session import Session
from getpass import getpass
from flask import redirect
import os
global user
#to do
#session cookies
#privalages
#

app = Flask(__name__)

bcrypt = Bcrypt(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #configuring base

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem" #configuring session
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(32))

db = SQLAlchemy(app)
Session(app)

class Profile(db.Model): #setting up sql
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),unique=False,nullable=False)
    password = db.Column(db.String(128),unique=False,nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"username : {self.username}"

@app.cli.command("create-admin")
def create_admin():
    username = input("write admin username: ")
    if Profile.query.filter_by(username=username).first():
        print("That username already exists.")
        return
    password = getpass("Password: ")
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    user = Profile(username=username,password=hashed ,is_admin=True)

    db.session.add(user)
    db.session.commit()
    print("admin user created")

@app.cli.command("delete-admin")
def delete_admin():
    username = input("write admin username: ")
    data = Profile.query.filter_by(username=username).first()
    if data==None:
        print("no admin found")
        return
    
    print("are you sure? [y/n]")
    ans = input()

    if ans == "y":
        db.session.delete(data)
        db.session.commit()
        print("admin removed")

    else:
        print("aborted")

@app.cli.command("list-admins")
def list_admins():
    data = Profile.query.filter_by(is_admin=True)
    for i in data:
        print(i.username)

@app.route("/",methods=["GET","POST"])
def main_page():
    return render_template("mainpage.html")


@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"] #getting userdata
    
        if username != '' and password != '':
            user = Profile.query.filter_by(username=username).first() #getting base data

            if user is None:
                print('user not found')
                return render_template("notfound_user.html")

            user_1 = bcrypt.check_password_hash(user.password, password) #checking passwords

            if user_1 and user.is_admin:
                session["user_id"] = user.id
                session["is_admin"] = user.is_admin
                print("admin login")
                return redirect('/admin')

            elif user_1:
                print('login successful')
                session["user_id"] = user.id
                return redirect(f"/user/{user.id}")
            
            else:
                print('wrong password')
                return render_template("log_in.html",error="Wrong username or password")

    return render_template("log_in.html")

@app.route("/signin",methods=["GET","POST"])
def signin():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]

        hashed = bcrypt.generate_password_hash(password).decode('utf-8') #hashing passwords

        if username != '' and password != '':
            p = Profile(username=username, password=hashed) #saving in sql
            db.session.add(p)
            db.session.commit()
            user = Profile.query.filter_by(username=username).first()
            return redirect(f"/user/{user.id}")

    return render_template("sign_in.html")

@app.route("/admin",methods=["GET","POST"])
def admin_panel():
    if not session.get("is_admin"):
        return redirect("/")
    profiles = Profile.query.all()
    print("admin accesing page")

    return render_template('admin_panel.html', profiles=profiles)

@app.route("/logout")
def loging_out():
    print("admin/user loging out")
    session.clear()
    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    if not session.get("is_admin"):
        return redirect("/")
    data = db.session.get(Profile, id)
    db.session.delete(data)
    db.session.commit()
    return redirect("/admin")

@app.route("/edit/<int:id>",methods=["POST","GET"])
def edit(id):
    if not session.get("is_admin"):
        return redirect("/")
    data = db.session.get(Profile,id)
    if request.method=="POST":
        new_username = request.form["username"]
        new_password = request.form["password"]

        if not(new_username==""):
            data.username = new_username
        if not(new_password==""):
            hashed = bcrypt.generate_password_hash(new_password).decode('utf-8')
            data.password = hashed
        
        db.session.commit()

        return redirect("/admin")

    return render_template("editing_user.html")

@app.route("/user/<int:id>")
def user_profile(id):
    user=Profile.query.filter_by(id=id).first()
    if not session.get("user_id")==user.id:
        return redirect("/")
    return render_template("user_profile.html",user=user)

if __name__ == "__main__":
    with app.app_context(): 
        db.create_all() 
    app.run(debug=True)