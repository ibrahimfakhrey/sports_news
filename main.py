from flask import Flask, render_template, request, redirect
import requests
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user


from flask_babel import Babel
app=Flask(__name__)

END_POINT="https://api.openweathermap.org/data/2.5/weather"


API_KEY="6ab73d57dd3ea5445996fd55de54ad44"
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # Check if user is in paid_user table
    user = User.query.get(int(user_id))
    if user:
        return user
    # If not, check if user is in free_user table

    # If user is not in either table, return None
    return None

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

babel = Babel(app)
with app.app_context():
    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        phone = db.Column(db.String(100), unique=True)
        password = db.Column(db.String(100))
        name = db.Column(db.String(1000))
        role = db.Column(db.String(1000), default="user")
        last_search_time = db.Column(db.DateTime, default=datetime.utcnow)
        search_count = db.Column(db.Integer, default=0)







    db.create_all()


class MyModelView(ModelView):
    def is_accessible(self):
            return True

admin = Admin(app)
admin.add_view(MyModelView(User, db.session))

data={}
@app.route("/t",methods=["GET","POST"])
def start():
    if current_user.is_authenticated and current_user.role=="user":
        city_name = "banha"
        if request.method=="POST":
            if current_user.search_count <3:
                current_user.search_count+=1
                current_user.last_search_time = datetime.utcnow()
                db.session.commit()
                city_name=request.form.get("city_name")
                print(city_name)
                params = {
                    'appid': API_KEY,
                    'q': city_name,  # You can also use 'q' parameter for city name
                    "units": "metric"
                }

                response=requests.get(END_POINT,params)
                temp=response.json()
                temp=temp["main"]["temp"]




                return render_template("index.html",t=int(temp))
            else:
                time_difference = datetime.utcnow() - current_user.last_search_time
                if time_difference > timedelta(minutes=15):
                    current_user.search_count==0
                    db.session.commit()
                    return redirect("/t")

                return"اصبر يا جحش "
    if current_user.is_authenticated and current_user.role=="admin":

        all_users=User.query.filter_by(role="user").all()

        return render_template("admindash.html",all_users=all_users)
    city_name="banha"
    params = {
        'appid': API_KEY,
        'q': city_name,  # You can also use 'q' parameter for city name
        "units": "metric"
    }
    today_date = datetime.utcnow().date()
    if current_user.is_authenticated:
        last_search_date=current_user.last_search_time.date()
        if last_search_date < today_date:
            current_user.search_count=0
            db.session.commit()


        response = requests.get(END_POINT, params)
        temp = response.json()
        temp = temp["main"]["temp"]

        return render_template("index.html", t=int(temp))
    else:
        return redirect("/login")


@app.route("/")
def s():
    return render_template("dash.html")
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        user_name=request.form.get("user_name")
        password= generate_password_hash(request.form.get("password"), method='pbkdf2:sha256',salt_length=8

            )
        new_user=User(
            phone=user_name,
            password=password
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        target=User.query.filter_by(phone=user_name).first()
        if target and check_password_hash( target.password,password):
            login_user(target)
            return redirect("/")
        else:
           return redirect("/register")


    return render_template("login.html")
@app.route("/get_questions")
def get_questions():
    params={
        "amount":10,
        "category":21
    }
    response=requests.get(url="https://opentdb.com/api.php",params=params)
    return response.json()
@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")

if __name__ =="__main__":
    app.run(debug=True)