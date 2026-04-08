from flask import Flask, request, send_from_directory
import os
import uuid
import json
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
META_FILE = os.path.join(BASE_DIR, "uploads_meta.json")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ADMIN_KEY = "mysecretgallery"

if not os.path.exists(META_FILE):
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)


def load_meta():
    with open(META_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_meta(data):
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ================= UPLOAD PAGE =================
UPLOAD_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body {
    margin:0;
    font-family:Arial;
    color:white;
    background: linear-gradient(135deg,#140014,#250028,#3a0a46);
    padding:20px;
}

.container {
    max-width:600px;
    margin:auto;
    background:rgba(255,255,255,0.08);
    padding:20px;
    border-radius:20px;
    box-shadow:0 0 20px hotpink;
}

h1 {
    text-align:center;
    color:#ffb3e6;
}

input, textarea {
    width:100%;
    margin:10px 0;
    padding:12px;
    border-radius:10px;
    border:none;
}

button {
    width:100%;
    padding:12px;
    border:none;
    border-radius:12px;
    background:hotpink;
    color:white;
    font-weight:bold;
}
</style>
</head>
<body>

<div class="container">
<h1>Upload Your Pics 💕</h1>

<form method="POST" enctype="multipart/form-data">
<input type="text" name="name" placeholder="Your name (optional)">
<textarea name="message" placeholder="Leave a message 💬"></textarea>
<input type="file" name="photos" multiple required>
<button type="submit">Upload 💗</button>
</form>

</div>

</body>
</html>
"""

THANK_YOU_HTML = """
<h1 style="text-align:center;color:white;">Uploaded! 💖</h1>
<a href="/" style="display:block;text-align:center;color:white;">Upload more</a>
"""

@app.route("/", methods=["GET","POST"])
def upload():
    if request.method == "POST":
        files = request.files.getlist("photos")
        name = request.form.get("name","")
        message = request.form.get("message","")

        meta = load_meta()

        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                unique = str(uuid.uuid4()) + "_" + filename
                file.save(os.path.join(UPLOAD_FOLDER, unique))

                meta.append({
                    "file": unique,
                    "name": name,
                    "message": message,
                    "time": datetime.now().strftime("%I:%M %p")
                })

        save_meta(meta)
        return THANK_YOU_HTML

    return UPLOAD_HTML


# ================= GALLERY =================
@app.route("/gallery")
def gallery():
    key = request.args.get("key")
    if key != ADMIN_KEY:
        return "Access denied"

    meta = list(reversed(load_meta()))

    cards = ""
    for item in meta:
        cards += f"""
        <div class="card">
            <img src="/uploads/{item['file']}">
            <div class="info">
                <b>{item.get('name') or "Guest"}</b><br>
                {item.get('message') or ""}
            </div>
        </div>
        """

    return f"""
    <html>
    <head>
    <meta http-equiv="refresh" content="20">
    <style>
    body {{
        background:#1a001f;
        color:white;
        font-family:Arial;
    }}
    .grid {{
        display:grid;
        grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
        gap:15px;
    }}
    .card img {{
        width:100%;
        height:200px;
        object-fit:cover;
    }}
    </style>
    </head>
    <body>
    <h1>Gallery 💕</h1>
    <div class="grid">{cards}</div>
    </body>
    </html>
    """


# ================= SLIDESHOW =================
@app.route("/slideshow")
def slideshow():
    key = request.args.get("key")
    if key != ADMIN_KEY:
        return "Access denied"

    meta = list(reversed(load_meta()))

    slides = []
    for item in meta:
        slides.append({
            "img": f"/uploads/{item['file']}",
            "name": item.get("name") or "Guest",
            "msg": item.get("message") or ""
        })

    first = slides[0] if slides else {"img":"","name":"","msg":""}

    return f"""
    <html>
    <head>
    <meta http-equiv="refresh" content="30">
    <style>
    body {{
        margin:0;
        background:black;
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        color:white;
    }}
    img {{
        max-width:90%;
        max-height:80%;
        border-radius:20px;
        transition:opacity 1s;
    }}
    .caption {{
        position:absolute;
        bottom:20px;
        background:rgba(0,0,0,0.5);
        padding:10px;
        border-radius:10px;
    }}
    </style>
    </head>

    <body>
    <img id="slide" src="{first['img']}">
    <div class="caption">
        <div id="name">{first['name']}</div>
        <div id="msg">{first['msg']}</div>
    </div>

    <script>
    const slides = {json.dumps(slides)};
    let i = 0;

    const img = document.getElementById("slide");
    const name = document.getElementById("name");
    const msg = document.getElementById("msg");

    setInterval(() => {{
        if(slides.length === 0) return;

        img.style.opacity = 0;

        setTimeout(() => {{
            i = (i + 1) % slides.length;
            img.src = slides[i].img;
            name.textContent = slides[i].name;
            msg.textContent = slides[i].msg;
            img.style.opacity = 1;
        }}, 1000);

    }}, 10000);
    </script>

    </body>
    </html>
    """


# ================= SERVE FILES =================
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True)