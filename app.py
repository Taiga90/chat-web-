from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit, join_room
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
    c.execute("""
        CREATE TABLE IF NOT EXISTS dm_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id TEXT,
            sender TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
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
# DMルームID生成
# -------------------
def make_dm_room(user1, user2):
    users = sorted([user1, user2])
    return f"dm_{users[0]}_{users[1]}"

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
# DM一覧ページ
# -------------------
@app.route("/dm")
@login_required
def dm_list():
    current = session["user"]
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username != ?", (current,))
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return render_template("dm_list.html", username=current, users=users)

# -------------------
# 個別DMページ
# -------------------
@app.route("/dm/<target>")
@login_required
def dm(target):
    current = session["user"]
    room_id = make_dm_room(current, target)

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT sender, message, timestamp FROM dm_messages WHERE room_id=? ORDER BY id ASC", (room_id,))
    messages = c.fetchall()
    conn.close()

    return render_template("dm.html",
                           username=current,
                           target=target,
                           room_id=room_id,
                           messages=messages)

# -------------------
# 画像アップロード（全体チャット用）
# -------------------
@app.route("/upload", methods=["POST"])
@login_required
def upload():
    file = request.files["image"]
    filename = file.filename
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    socketio.emit("image", {
        "user": session["user"],
        "url": f"/static/uploads/{filename}"
    }, broadcast=True)

    return "OK"

# -------------------
# Socket.IO（全体チャット）
# -------------------
@socketio.on("message")
def handle_message(data):
    emit("message", data, broadcast=True)

# -------------------
# Socket.IO（DM用）
# -------------------
@socketio.on("join_dm")
def join_dm(data):
    room_id = data["room_id"]
    join_room(room_id)

@socketio.on("dm_message")
def dm_message(data):
    room_id = data["room_id"]
    sender = data["user"]
    text = data["text"]

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO dm_messages(room_id, sender, message) VALUES (?, ?, ?)",
              (room_id, sender, text))
    conn.commit()
    conn.close()

    emit("dm_message", data, room=room_id)

# -------------------
# 起動
# -------------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
