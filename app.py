from flask import Flask, render_template,request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 

app = Flask(__name__)

bcrypt = Bcrypt(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #configuring base

db = SQLAlchemy(app)

class Profile(db.Model): #setting up sql
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),unique=False,nullable=False)
    password = db.Column(db.String(20),unique=False,nullable=False)

    

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

            if user_1:
                print('login successful')
                return render_template("welcome_ou.html")
            else:
                print('wrong password')
                return render_template("wrong_password.html")


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
            return render_template("welcome_nu.html")

    return render_template("sign_in.html")

if __name__ == "__main__":
    with app.app_context(): 
        db.create_all() 
    app.run(debug=True)