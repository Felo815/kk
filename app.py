from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# إعداد قاعدة البيانات SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecret'  # مفتاح التشفير للجلسات

db = SQLAlchemy(app)

# جدول المستخدمين
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # admin أو user

# جدول النقاط
class Points(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, default=0)

# إنشاء الجداول
with app.app_context():
    db.create_all()

# صفحة تسجيل الدخول
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # التحقق من المستخدم
        admin_passwords = ['felo', 'gad', 'elrab']
        user_passwords = ['elnor', 'abona']

        if password in admin_passwords:
            session['user'] = username
            session['role'] = 'admin'
            return redirect(url_for('dashboard'))
        elif password in user_passwords:
            session['user'] = username
            session['role'] = 'user'
            return redirect(url_for('dashboard'))
        else:
            return render_template('index.html', error="كلمة السر غير صحيحة!")

    return render_template('index.html')

# الصفحة المشتركة بين المسؤول والمستخدم
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('felo.html')

# صفحة عرض النقاط وإضافة أسماء جديدة
@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST' and session.get('role') == 'admin':
        name = request.form['name']
        if name:
            new_user = Points(name=name, points=0)  # يبدأ بـ 0 نقاط
            db.session.add(new_user)
            db.session.commit()

    users = Points.query.all()
    return render_template('home.html', users=users, role=session.get('role'))

# تعديل النقاط (للمسؤول فقط)
@app.route('/update_points/<int:user_id>/<int:change>')
def update_points(user_id, change):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))

    user = Points.query.get(user_id)
    if user:
        user.points += change
        db.session.commit()

    return redirect(url_for('home'))

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__== '__main__':
    app.run(debug=True)