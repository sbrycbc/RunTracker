import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import random

app = Flask(__name__)

# .env dosyasını yükle
load_dotenv()

# API anahtarını .env dosyasından al
API_KEY = os.getenv('API_KEY')
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'

# Ana sayfa
@app.route('/', methods=['GET', 'POST'])
def home():
    temperature = None
    weather_description = None
    suggestion = None
    city = None

    if request.method == 'POST':
        if 'show_weather' in request.form:  # Hava durumu formu tıklama
            return render_template('home.html', show_weather_form=True)
        elif 'city' in request.form:  # Şehir girildiyse hava durumu al
            city = request.form['city']
            city = city.capitalize()  # Şehir ismini ilk harfini büyük yapmak için
            temperature, weather_description = get_weather(city)

            # Hava durumu açıklamasını düzenle
            if weather_description:
                weather_description = weather_description.title()

            # Hava durumu önerisi
            if temperature is not None:
                if temperature < 10:
                    suggestion = "Bugün hava soğuk, kalin giyin!"
                elif temperature > 30:
                    suggestion = "Bugün hava çok sicak, hafif giyinin!"
                else:
                    suggestion = "Bugün hava güzel, rahatça kosmaya çikabilirsiniz."
            
            return render_template('home.html', temperature=temperature, weather_description=weather_description, suggestion=suggestion, city=city)

    return render_template('home.html', show_weather_form=False)


# BMI Hesaplama
@app.route('/bmi', methods=['GET', 'POST'])
def bmi():
    if request.method == 'POST':
        height = float(request.form['height']) / 100  # Boyu metreye çevir
        weight = float(request.form['weight'])
        bmi = round(weight / (height ** 2), 2)

        # BMI durumu
        if bmi < 18.5:
            status = "Zayif"
        elif 18.5 <= bmi < 24.9:
            status = "Normal"
        elif 25 <= bmi < 29.9:
            status = "Fazla Kilolu"
        else:
            status = "Obez"

        return render_template('bmi.html', bmi=bmi, status=status)
    return render_template('bmi.html')

# Koşu takibi
@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    if request.method == 'POST':
        distance = request.form['distance']
        duration = request.form['duration']
        calories = request.form['calories']
        # Hedef hız önerisi (örnek: 10 km/saat)
        speed = round(float(distance) / (float(duration) / 60), 2)
        motivation = random.choice([
            "Harika gidiyorsun! Aynen devam et!",
            "Bugün küçük bir adim at, yarin büyük bir hedefe ulaş!",
            "Koşmaya devam et, hedeflerine bir adim daha yaklaştin!"
        ])
        return render_template('tracker.html', distance=distance, duration=duration, calories=calories, speed=speed, motivation=motivation)

    return render_template('tracker.html')

# Hava durumu için fonksiyon
def get_weather(city):
    url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric&lang=tr"  # 'units=metric' sıcaklığı Celsius cinsinden alır
    response = requests.get(url)
    data = response.json()

    if data["cod"] != "404":
        main_data = data["main"]
        weather_data = data["weather"][0]
        temperature = main_data["temp"]
        weather_description = weather_data["description"]
        return temperature, weather_description
    else:
        return None, None

if __name__ == "__main__":
    app.run(debug=True)
