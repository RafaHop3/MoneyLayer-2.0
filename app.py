import os
import stripe
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'segredo_super_secreto' 

stripe.api_key = os.environ.get("STRIPE_API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

class User(UserMixin):
    def __init__(self, id, nickname, is_admin):
        self.id = id
        self.nickname = nickname
        self.is_admin = is_admin 

class Company:
    def __init__(self, id, name, company_type, balance):
        self.id = id
        self.name = name
        self.company_type = company_type
        self.balance = balance

@login_manager.user_loader
def load_user(user_id):
    if not DATABASE_URL: return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT id, nickname, is_admin FROM users WHERE id = %s", (user_id,))
        data = cur.fetchone()
        conn.close()
        if data:
            return User(id=data[0], nickname=data[1], is_admin=data[2])
    except:
        return None
    return None

def get_user_company(user_id):
    if not DATABASE_URL: return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT id, name, company_type, balance FROM companies WHERE user_id = %s", (user_id,))
        data = cur.fetchone()
        conn.close()
        if data:
            return Company(id=data[0], name=data[1], company_type=data[2], balance=data[3])
    except:
        return None
    return None

@app.route('/')
def index():
    if current_user.is_authenticated:
        my_company = get_user_company(current_user.id)
        return render_template('dashboard.html', user=current_user, company=my_company)
    return render_template('login_gate.html')

@app.route('/invoice')
@login_required
def invoice():
    company = get_user_company(current_user.id)
    if not company:
        flash("Registre sua empresa primeiro!")
        return redirect(url_for('index'))
    return render_template('invoice.html', company=company)

@app.route('/billing')
@login_required
def billing():
    company = get_user_company(current_user.id)
    if not company:
        flash("Registre sua empresa primeiro!")
        return redirect(url_for('index'))
    return render_template('billing.html', company=company)

@app.route('/register_company', methods=['POST'])
@login_required
def register_company():
    name = request.form['company_name']
    tax_id = request.form['tax_id']
    c_type = request.form['company_type']
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT id FROM companies WHERE user_id = %s", (current_user.id,))
    if cur.fetchone():
        flash('Você já possui uma empresa registrada!')
    else:
        cur.execute("INSERT INTO companies (user_id, name, tax_id, company_type) VALUES (%s, %s, %s, %s)", (current_user.id, name, tax_id, c_type))
        conn.commit()
        flash('Empresa registrada com sucesso!')
    conn.close()
    return redirect(url_for('index'))

@app.route('/register', methods=['POST'])
def register():
    nickname = request.form['nickname']
    password = request.form['password']
    confirm = request.form['confirm_password']
    if password != confirm:
        flash('As senhas não conferem!')
        return redirect(url_for('index'))
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE nickname = %s", (nickname,))
    if cur.fetchone():
        flash('Nickname já existe!')
        conn.close()
        return redirect(url_for('index'))
    hashed_password = generate_password_hash(password)
    cur.execute("INSERT INTO users (nickname, password_hash, is_admin) VALUES (%s, %s, FALSE)", (nickname, hashed_password))
    conn.commit()
    conn.close()
    flash('Conta criada! Faça login.')
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    nickname = request.form['nickname']
    password = request.form['password']
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT id, nickname, password_hash, is_admin FROM users WHERE nickname = %s", (nickname,))
    data = cur.fetchone()
    conn.close()
    if data and check_password_hash(data[2], password):
        user = User(id=data[0], nickname=data[1], is_admin=data[3])
        login_user(user)
        return redirect(url_for('index'))
    flash('Login falhou.')
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash("Acesso Negado!")
        return redirect(url_for('index'))
    return "<h1>Área Master</h1><p>Controle Global</p><a href='/'>Voltar</a>"

if __name__ == '__main__':
    app.run(port=3000, debug=True)
