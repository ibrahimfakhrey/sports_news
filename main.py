from flask import Flask, render_template, request, redirect
import requests

app=Flask(__name__)

END_POINT="https://api.openweathermap.org/data/2.5/weather"


API_KEY="6ab73d57dd3ea5445996fd55de54ad44"
data={

}
@app.route("/t",methods=["GET","POST"])
def start():
    city_name = "banha"
    if request.method=="POST":
        print("i am in post mode ")
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
    print(temp)



    return render_template("index.html",t=int(temp))

@app.route("/")
def s():
    return "home"
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        user_name=request.form.get("user_name")
        password=request.form.get("password")
        print(f" i am in post mode and i recived {user_name} and the {password}")
        data[user_name]=password
        print(data)
        return redirect("/login")
    return render_template("register.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        print(data)
        print(password)
        if user_name in data and data[user_name]==password:
            return redirect("/t")
        else:
           return redirect("/register")


    return render_template("login.html")


if __name__ =="__main__":
    app.run(debug=True)