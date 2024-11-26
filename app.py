import requests
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import os
import random
import csv
import hashlib
import secrets

app = Flask(__name__)

# .env dosyasını yükle
load_dotenv()



# API anahtarını .env dosyasından al
API_KEY = os.getenv('API_KEY')
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'
SECRET_KEY = os.getenv('SECRET_KEY')

# CSV dosyasının yolu
CSV_FILE = 'users.csv'

app.secret_key = SECRET_KEY

# Global koşu verisi listesi
run_logs = []

# Kullanıcıyı CSV dosyasına kaydetme
def save_user_to_csv(name, email, username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    with open('users.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([name, email, username, hashed_password])

# Kullanıcının CSV dosyasında kayıtlı olup olmadığını kontrol etme
def check_if_user_exists(email, username):
    try:
        with open('users.csv', mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 3: 
                    if row[1] == email or row[2] == username:  
                        return True
    except FileNotFoundError:
        # Dosya bulunamadığında False döndür
        return False
    return False


# Kullanıcı bilgilerini CSV dosyasından okuma fonksiyonu
def read_users_from_csv():
    users = []
    try:
        with open('users.csv', mode='r', encoding='utf-8') as file:  # Dosya adı burada 'users.csv' olarak belirtilmeli
            reader = csv.reader(file)
            users = [row for row in reader]  # Tüm kullanıcıları liste olarak döndür
    except FileNotFoundError:
        # Eğer CSV dosyası bulunamazsa boş bir liste döner
        pass
    return users


# Ana sayfa
@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

# Kullanıcı kaydetme
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        # Şifrelerin eşleşip eşleşmediğini kontrol et
        if password != password_confirm:
            return "Şifreler eşleşmiyor, lütfen tekrar deneyin."

        # Kullanıcının e-posta ve kullanıcı adı ile daha önce kaydedilip edilmediğini kontrol et
        if check_if_user_exists(email, username):
            return "Bu e-posta veya kullanıcı adı zaten kullanılıyor."

        # Kullanıcıyı CSV'ye kaydet
        save_user_to_csv(name, email, username, password)

        # Kaydettikten sonra login sayfasına yönlendir
        return redirect(url_for('login'))

    return render_template('register.html')

# Kullanıcıyı kullanıcı adı ve şifre ile doğrulama
def check_user_credentials(username, password):
    try:
        with open('users.csv', mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 4:  # Eğer veri eksikse atla
                    continue
                
                stored_username = row[2]  # CSV'deki kullanıcı adı
                stored_password = row[3]  # CSV'deki hash'lenmiş şifre

                # Şifreyi hash'leyip kontrol ediyoruz
                if stored_username == username and stored_password == hashlib.sha256(password.encode()).hexdigest():
                    return row  # Kullanıcı bulundu, geri döndür
    except FileNotFoundError:
        return None
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']  # Kullanıcı adı alıyoruz
        password = request.form['password']  # Şifre alıyoruz

        # Kullanıcıyı kontrol et (CSV'den okuma)
        user = check_user_credentials(username, password)

        if user:
            # Kullanıcı doğru bilgileri girdiyse giriş yap
            session['logged_in'] = True
            session['username'] = username  # Kullanıcıyı tanımlamak için kullanıcı adı kullanıyoruz
            return redirect(url_for('tracker'))  # Ana sayfaya yönlendir
        else:
            return "Geçersiz kullanıcı adı veya şifre."

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()  # Tüm session bilgilerini temizle
    return redirect(url_for('home'))  # Ana sayfaya yönlendir


# Kullanıcıları listeleme
@app.route('/users')
def user_list():
    users = read_users_from_csv()  # CSV dosyasındaki kullanıcıları oku
    return render_template('users.html', users=users)

# Hava durumu verisini alma fonksiyonu
def get_weather(city):
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
    if temperature > 35:
        return "Bugün hava cok sıcak, yanina bol su almayi unutmayin!!"
    elif 25 <= temperature <= 35:
        return "Bugün hava biraz sıcak, hafif tempoda koşmayı düşünün!!"
    elif 15 <= temperature < 25:
        return "Hava harika..Bu gün kacmaz!!"
    elif 5 <= temperature <15:
        return "Koşu için güzel bir gün!!"
    elif 0 <= temperature < 5:
        return "Havalar sogumaya basliyor..Ayakkabi ve kiyafetlere dikkat!!"
    else:
        return "Hava soğuk, kalin giyinmeyi unutmayın!!"

# Hava durumu sayfası
@app.route('/weather', methods=['GET', 'POST'])
def weather():
    city = None
    temperature = None
    weather_description = None
    suggestion = None

    if request.method == 'POST':  
        city = request.form.get('city') 

        if city:  
            city = city.strip().title()
            temperature, weather_description = get_weather(city)

            if temperature is not None: 
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
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))  # Kullanıcı giriş yapmamışsa giriş sayfasına yönlendir

    username = session['username'].title()  # Kullanıcı adı oturumdan alınıyor

    # Koşu verilerini CSV'den oku ve session'a kaydet
    run_data = read_run_data_from_csv(username)
    session['run_logs'] = run_data  # CSV'deki verileri session'a yüklüyoruz

    if request.method == 'POST':
        # Formdan gelen verileri alalım
        distance = request.form.get('distance')  # Mesafe
        duration = request.form.get('duration')  # Süre
        calories = request.form.get('calories')  # Kalori

        if distance and duration and calories:
            distance = float(distance)
            duration = float(duration)
            calories = float(calories)

            # Hız hesaplama (km/saat)
            speed = round(duration / distance, 2)


            # Koşu verisini session'a kaydediyoruz
            run_log = {
                "distance": distance,
                "duration": duration,
                "calories": calories,
                "speed": speed
            }

            # Koşu verilerini session'a ekleyelim
            if 'run_logs' not in session:
                session['run_logs'] = []  # Eğer run_logs yoksa başlatıyoruz.
            session['run_logs'].append(run_log)  # Yeni koşuyu listeye ekliyoruz.

            # Koşu verilerini CSV'ye kaydedelim
            save_run_data_to_csv(username, distance, duration, calories)

            # Motivasyon mesajı
            motivation = random.choice([
                "Harika gidiyorsun! Aynen devam et!",
                "Bugün küçük bir adım at, yarın büyük bir hedefe ulaş!",
                "Koşmaya devam et, hedeflerine bir adım daha yaklaştın!",
                "Bugün koştuğun mesafe, yarının gücüdür!",
                "Ufak adımlar büyük başarılara götürür. Koşmaya devam et!",
                "Hedeflerin için sadece bir koşu uzaktasın!",
                "Zihnin 'dur' dediğinde, bedenin 'biraz daha' diyebilir.",
                "Koşarken ayakların yorulsa bile ruhun hep özgür olsun!",
                "Bazen yavaş koş, bazen hızlı; ama her zaman ilerle.",
                "Bir maraton bir adımla başlar, bir efsane azimle doğar!"
            ])

            # Verileri template'e gönderiyoruz
            return render_template('tracker.html', username=username, distance=distance,
                                   duration=duration, calories=calories, speed=speed,
                                   motivation=motivation)

        else:
            return "Lütfen tüm alanları doldurun", 400  # Hata mesajı

    # Sayfa yüklendiğinde verileri oku
    return render_template('tracker.html', username=username, run_logs=session['run_logs'])

# Koşu verilerini CSV dosyasına kaydetme
def save_run_data_to_csv(username, distance, duration, calories):
    file_name = f"{username}_run_data.csv"
    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([distance, duration, calories])


# Koşu verilerini CSV dosyasından okuma
def read_run_data_from_csv(username):
    file_name = f"{username}_run_data.csv"
    runs = []
    try:
        with open(file_name, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                # CSV'den alınan her koşu için hız hesaplanır
                runs.append({
                    "distance": float(row[0]),
                    "duration": float(row[1]),
                    "calories": float(row[2]),
                    "speed": round(float(row[0]) / (float(row[1]) / 60), 2)
                })
    except FileNotFoundError:
        pass  # Eğer dosya yoksa, hatayı yakala ve boş döndür
    return runs


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
    average_speed = round(total_distance / (total_duration ), 2)  if total_duration > 0 else 0

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
    username = session['username'].title()

    # Koşu verilerini CSV dosyasından oku
    run_data = read_run_data_from_csv(username)

    if not run_data:
        return render_template("performance.html", message="Henüz bir koşu kaydedilmedi.")

    # Toplam değerler
    total_distance = sum(log["distance"] for log in run_data)
    total_duration = sum(log["duration"] for log in run_data)
    total_calories = sum(log["calories"] for log in run_data)

    # Ortalama hız
    average_speed = round(total_distance / (total_duration), 2) if total_duration > 0 else 0

    # En uzun koşu
    longest_run = max(run_data, key=lambda log: log["distance"], default=None)

    return render_template(
        "performance.html",
        run_logs=run_data,
        total_distance=total_distance,
        total_duration=total_duration,
        total_calories=total_calories,
        average_speed=average_speed,
        longest_run=longest_run,
    )

if __name__ == "__main__":
    app.run(debug=True)
