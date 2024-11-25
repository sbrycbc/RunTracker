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
run_logs = []

# Hava durumu verisini alma fonksiyonu
def get_weather(city):
    """Şehir adını kullanarak API'den hava durumu verisi çeker."""
    url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric&lang=tr"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != "404":
        temperature = data["main"]["temp"]
        weather_description = data["weather"][0]["description"].title()
        return temperature, weather_description
    return None, None

# Hava durumu önerisi belirleme fonksiyonu
def get_weather_suggestion(temperature):
    """Sıcaklığa göre koşu önerisi döner."""
    if temperature > 25:
        return "Bugün hava sıcak, hafif tempoda koşmayı düşünün!"
    elif 15 <= temperature <= 25:
        return "Koşu için harika bir gün!"
    else:
        return "Hava soğuk, sıcak kalmayı unutmayın!"

# Ana sayfa
@app.route('/', methods=['GET'])
def home():
    """Ana sayfa: Hoşgeldiniz mesajı ve yönlendirme bağlantıları içerir."""
    return render_template('home.html')

# Hava durumu sayfası
@app.route('/weather', methods=['GET', 'POST'])
def weather():
    """Hava durumu sayfası: Kullanıcının girdiği şehir için hava durumu verir."""
    city = None
    temperature = None
    weather_description = None
    suggestion = None

    if request.method == 'POST':  # Şehir bilgisi gönderilmişse
        city = request.form.get('city')  # Kullanıcının girdiği şehir adı

        if city:  # Eğer şehir boş değilse hava durumu alınır
            city = city.strip().title()
            temperature, weather_description = get_weather(city)

            if temperature is not None:  # Geçerli veri varsa öneri oluştur
                suggestion = get_weather_suggestion(temperature)
            else:
                suggestion = "Geçersiz bir şehir adı girdiniz. Lütfen tekrar deneyin."

    return render_template('weather.html', temperature=temperature, weather_description=weather_description, suggestion=suggestion, city=city)

# BMI Hesaplama
@app.route('/bmi', methods=['GET', 'POST'])
def bmi():
    if request.method == 'POST':
        height = float(request.form['height']) / 100  # Boyu metreye çevir
        weight = float(request.form['weight'])
        bmi = round(weight / (height ** 2), 2)

        # BMI durumu
        if bmi < 18.5:
            status = "Sonuçlarınız, BMI'nizin düşük olduğunu gösteriyor."
        elif 18.5 <= bmi < 24.9:
            status = "Harika! BMI'niz sağlıklı bir aralıkta."
        elif 25 <= bmi < 29.9:
            status = "Sonuçlarınız, BMI'nizin biraz yüksek olduğunu gösteriyor."
        else:
            status = "Sonuçlarınız, BMI'nizin obezite seviyesinde olduğunu gösteriyor."
            
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
            "Bugün küçük bir adım at, yarın büyük bir hedefe ulaş!",
            "Koşmaya devam et, hedeflerine bir adım daha yaklaştın!"
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
