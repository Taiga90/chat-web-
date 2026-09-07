from flask import Flask, render_template, request, redirect, session, send_from_directory
from flask_socketio import SocketIO, emit
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------
# DB 初期化
# -------------------
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -------------------
# ログイン必須
# -------------------
def login_required(func):
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# -------------------
# ルーティング
# -------------------
@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/chat")
        else:
            return render_template("login.html", error="ログイン失敗")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            c.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            return render_template("register.html", error="そのユーザー名は使えません")

    return render_template("register.html")

@app.route("/chat")
@login_required
def chat():
    return render_template("chat.html", username=session["user"])

# -------------------
# 画像アップロード
# -------------------
@app.route("/upload", methods=["POST"])
@login_required
def upload():
    file = request.files["image"]
    filename = file.filename
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    # SocketIOで画像メッセージを送信
    socketio.emit("image", {
        "user": session["user"],
        "url": f"/static/uploads/{filename}"
    }, broadcast=True)

    return "OK"

# -------------------
# テキストメッセージ
# -------------------
@socketio.on("message")
def handle_message(data):
    emit("message", data, broadcast=True)

# -------------------
# 起動
# -------------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
