from flask import Flask, render_template, request
import requests  # Hava durumu için
import random

app = Flask(__name__)

# Ana sayfa
@app.route('/')
def home():
    return render_template('home.html')

# BMI Hesaplama
@app.route('/bmi', methods=['GET', 'POST'])
def bmi():
    if request.method == 'POST':
        height = float(request.form['height']) / 100  # Boyu metreye çevir
        weight = float(request.form['weight'])
        bmi = round(weight / (height ** 2), 2)

        # BMI durumu
        if bmi < 18.5:
            status = "Zayıf"
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

# Hava durumu (Örnek: API kullanımı)
@app.route('/weather', methods=['GET'])
def weather():
    # Örnek: Hava durumu API'sinden veri çekelim (OpenWeatherMap gibi)
    city = request.args.get('city', 'Istanbul')  # Varsayılan şehir
    api_key = "API_KEY_HERE"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url).json()

    if response.get("cod") != 200:
        return "Hava durumu bilgisi alinamadi!"

    weather_desc = response["weather"][0]["description"]
    temperature = response["main"]["temp"]
    return render_template('home.html', weather=f"{city}: {weather_desc}, {temperature}°C")

if __name__ == '__main__':
    app.run(debug=True)
