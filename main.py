from flask import Flask,render_template
import requests

app=Flask(__name__)

END_POINT="https://api.openweathermap.org/data/2.5/weather"
API_KEY="6ab73d57dd3ea5445996fd55de54ad44"
params = {
    'appid': API_KEY,
    'q': "banha" ,# You can also use 'q' parameter for city name
    "units":"metric"
}
@app.route("/")
def start():

    response=requests.get(END_POINT,params)
    temp=response.json()
    temp=temp["main"]["temp"]
    print(temp)



    return render_template("index.html",t=int(temp))








if __name__ =="__main__":
    app.run(debug=True)