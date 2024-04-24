from flask import Flask,render_template,request
import requests

app=Flask(__name__)

END_POINT="https://api.openweathermap.org/data/2.5/weather"


API_KEY="6ab73d57dd3ea5445996fd55de54ad44"

@app.route("/",methods=["GET","POST"])
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








if __name__ =="__main__":
    app.run(debug=True)