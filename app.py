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

# Global koşu verisi listesi
run_logs = []  # Kullanıcıların koşu verilerini tutacak liste


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
    global run_logs
    if request.method == 'POST':
        distance = float(request.form['distance'])
        duration = float(request.form['duration'])
        calories = float(request.form['calories'])

        # Hız hesaplama
        speed = round(distance / (duration / 60), 2)  # km/saat cinsinden hız

        # Motivasyon mesajları
        motivation = random.choice([ 
            "Harika gidiyorsun! Aynen devam et!",
            "Bugün küçük bir adim at, yarin büyük bir hedefe ulaş!",
            "Koşmaya devam et, hedeflerine bir adim daha yaklaştin!"
        ])

        # Kullanıcının koşu verilerini listeye ekle
        run_logs.append({
            "distance": distance,
            "duration": duration,
            "calories": calories,
            "speed": speed
        })

        # Koşu analizini yap
        analysis = analyze_performance(run_logs)

        return render_template('tracker.html', distance=distance, duration=duration, calories=calories, speed=speed, motivation=motivation, analysis=analysis)

    return render_template('tracker.html')


# Performans analiz fonksiyonu
def analyze_performance(run_logs):
    # Toplam mesafe, süre ve hız
    total_distance = sum(log["distance"] for log in run_logs)
    total_duration = sum(log["duration"] for log in run_logs)
    total_speed = sum(log["speed"] for log in run_logs) / len(run_logs) if run_logs else 0

    # En hızlı koşu
    fastest_run = max(run_logs, key=lambda log: log["speed"], default=None)
    fastest_speed = fastest_run["speed"] if fastest_run else 0

    # Ortalama hız
    average_speed = round(total_distance / (total_duration / 60), 2) if total_duration > 0 else 0

    # Mesafe gelişimi: Son 3 koşunun mesafelerini topla
    recent_distance = sum(log["distance"] for log in run_logs[-3:])

    return {
        "total_distance": total_distance,
        "total_duration": total_duration,
        "average_speed": average_speed,
        "fastest_speed": fastest_speed,
        "recent_distance": recent_distance
    }


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


# Performans özet sayfası
@app.route('/performance', methods=['GET'])
def performance():
    global run_logs  # Global değişkeni kullanacağımızı belirtin

    # Toplam değerler
    total_distance = sum(log["distance"] for log in run_logs)
    total_duration = sum(log["duration"] for log in run_logs)
    total_calories = sum(log["calories"] for log in run_logs)

    # Ortalama hız
    average_speed = round(total_distance / (total_duration / 60), 2) if total_duration > 0 else 0

    # En uzun koşu
    longest_run = max(run_logs, key=lambda log: log["distance"], default=None)

    return render_template(
        "performance.html",
        run_logs=run_logs,
        total_distance=total_distance,
        total_duration=total_duration,
        total_calories=total_calories,
        average_speed=average_speed,
        longest_run=longest_run,
    )


if __name__ == "__main__":
    app.run(debug=True)
