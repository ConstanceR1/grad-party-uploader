# (FULL FINAL VERSION - DO NOT TRIM)

from flask import Flask, request, send_from_directory
import os, uuid, json
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
META_FILE = os.path.join(BASE_DIR, "uploads_meta.json")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ADMIN_KEY = "mysecretgallery"

if not os.path.exists(META_FILE):
    with open(META_FILE, "w") as f:
        json.dump([], f)

def load_meta():
    with open(META_FILE) as f:
        return json.load(f)

def save_meta(data):
    with open(META_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ---------------- UPLOAD ----------------
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
        return "<h1 style='color:white;text-align:center;'>Uploaded 💖</h1>"

    return """
    <body style="background:#140014;color:white;text-align:center;padding:40px;">
    <h1 style="color:#ffb3e6;">Upload Your Grad Pics 💕</h1>
    <form method="POST" enctype="multipart/form-data">
    <input type="text" name="name" placeholder="Your name"><br><br>
    <textarea name="message" placeholder="Leave a message 💬"></textarea><br><br>
    <input type="file" name="photos" multiple required><br><br>
    <button style="background:hotpink;color:white;padding:10px;border:none;">Upload 💗</button>
    </form>
    </body>
    """

# ---------------- GALLERY ----------------
@app.route("/gallery")
def gallery():
    if request.args.get("key") != ADMIN_KEY:
        return "Access denied"

    meta = list(reversed(load_meta()))

    cards = ""
    for item in meta:
        cards += f"""
        <div style="margin:10px">
        <img src="/uploads/{item['file']}" style="width:200px;border-radius:10px"><br>
        <b>{item.get('name') or 'Guest'}</b><br>
        {item.get('message') or ''}
        </div>
        """

    return f"""
    <body style="background:#1a001f;color:white;text-align:center;">
    <h1>Gallery 💕</h1>
    {cards}
    </body>
    """

# ---------------- SLIDESHOW ----------------
@app.route("/slideshow")
def slideshow():
    if request.args.get("key") != ADMIN_KEY:
        return "Access denied"

    meta = list(reversed(load_meta()))

    slides = [{
        "img": f"/uploads/{m['file']}",
        "name": m.get("name") or "Guest",
        "msg": m.get("message") or ""
    } for m in meta]

    first = slides[0] if slides else {"img":"","name":"","msg":""}

    return f"""
    <html>
    <head>
    <meta http-equiv="refresh" content="30">
    <style>

    body {{
        margin:0;
        overflow:hidden;
        background:black;
        font-family:Arial;
        color:white;
    }}

    .bg {{
        position:absolute;
        width:100%;
        height:100%;
        object-fit:cover;
        filter:blur(40px) brightness(0.6);
        transform:scale(1.2);
    }}

    .main {{
        position:absolute;
        width:100%;
        height:100%;
        display:flex;
        justify-content:center;
        align-items:center;
    }}

    .photo {{
        max-width:90%;
        max-height:80%;
        object-fit:contain;
        border-radius:20px;
        box-shadow:0 0 30px hotpink;
        transition:opacity 1s;
    }}

    .caption {{
        position:absolute;
        bottom:30px;
        background:rgba(0,0,0,0.5);
        padding:15px;
        border-radius:15px;
        text-align:center;
    }}

    </style>
    </head>

    <body>

    <img id="bg" class="bg" src="{first['img']}">

    <div class="main">
        <img id="photo" class="photo" src="{first['img']}">
    </div>

    <div class="caption">
        <div id="name">{first['name']}</div>
        <div id="msg">{first['msg']}</div>
    </div>

    <script>

    const slides = {json.dumps(slides)};
    let i = 0;

    const photo = document.getElementById("photo");
    const bg = document.getElementById("bg");
    const name = document.getElementById("name");
    const msg = document.getElementById("msg");

    setInterval(() => {{
        if(slides.length === 0) return;

        photo.style.opacity = 0;

        setTimeout(() => {{
            i = (i + 1) % slides.length;
            photo.src = slides[i].img;
            bg.src = slides[i].img;
            name.textContent = slides[i].name;
            msg.textContent = slides[i].msg;
            photo.style.opacity = 1;
        }}, 1000);

    }}, 10000);

    </script>

    </body>
    </html>
    """

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)