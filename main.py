from flask import Flask, render_template, request, redirect, jsonify
import requests
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

from datetime import datetime, date, timedelta
from sqlalchemy import and_
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


    class Quiz(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        phone = db.Column(db.String(100))
        taken_time = db.Column(db.DateTime, default=datetime.utcnow)
        amount_of_questions = db.Column(db.Integer, nullable=False)
        category = db.Column(db.String(100), nullable=False)
        mark = db.Column(db.Float, nullable=False)







    db.create_all()


class MyModelView(ModelView):
    def is_accessible(self):
            return True

admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Quiz, db.session))

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
    all_quizes=[]
    if current_user.is_authenticated :
        all_quizes=Quiz.query.filter_by(phone=current_user.phone).all()

    return render_template("dash.html",name="ali",q=len(all_quizes))
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
    amount = request.args.get('amount', default=10, type=int)  # Default to 10 if not provided
    category = request.args.get('category', default=21, type=int)  # Default to 21 if not provided
    print(f"i am in fetch and {amount} {category}")
    params = {
        "amount": amount,
        "category": category
    }
    response = requests.get(url="https://opentdb.com/api.php", params=params)
    data = response.json()
    results = data["results"]

    # Transform the data
    quizQuestions = []
    for item in results:
        question = item['question']
        correct_answer = item['correct_answer']
        incorrect_answers = item['incorrect_answers']

        # Combine correct and incorrect answers
        all_answers = incorrect_answers + [correct_answer]

        # Shuffle the answers to ensure the correct answer is not always last
        import random
        random.shuffle(all_answers)

        # Create answers dictionary
        answers = {chr(97 + i): answer for i, answer in enumerate(all_answers)}

        # Find the key for the correct answer
        correct_key = [key for key, value in answers.items() if value == correct_answer][0]

        # Append the formatted question to the quizQuestions list
        quizQuestions.append({
            "question": question,
            "answers": answers,
            "correctAnswer": correct_key
        })
    print(f"call hapens and here is the {quizQuestions}")

    # Return the transformed data as JSON
    return jsonify(quizQuestions)
@app.route("/takequiz",methods=["GET","POST"])
def take():
    if request.method=="POST":

        amount = request.form.get('amount')
        category = request.form.get('category')
        new_quiz=Quiz(
            phone=current_user.phone,
            amount_of_questions=amount,category=category,mark=0, taken_time=datetime.now()
        )
        db.session.add(new_quiz)
        db.session.commit()
        return render_template("quiz.html",ramy=amount,mahmoud=category)
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = today_start + timedelta(days=1)

    # Query the database
    quizzes_today = Quiz.query.filter(
        and_(
            Quiz.phone == current_user.phone,
            Quiz.taken_time >= today_start,
            Quiz.taken_time < today_end
        )
    ).all()

    if len(quizzes_today)> 2:
        return "sorry you reched the limit"
    return render_template("get_info.html")
@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")

if __name__ =="__main__":
    app.run(debug=True)