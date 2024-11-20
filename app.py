from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/submit', methods=['POST'])
def submit():
    age = request.form['age']
    weight = request.form['weight']
    target_weight = request.form['target_weight']
    
    return f"Yasiniz: {age}, Kilonuz: {weight}kg, Hedef Kilonuz: {target_weight}kg"

if __name__ == "__main__":
    app.run(debug=True)

