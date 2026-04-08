from flask import Flask, request, render_template_string, send_from_directory
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


UPLOAD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Upload Pics 💖</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            color: white;
            background:
                radial-gradient(circle at top left, rgba(255,105,180,0.28), transparent 25%),
                radial-gradient(circle at bottom right, rgba(255,20,147,0.22), transparent 25%),
                linear-gradient(135deg, #140014, #250028 40%, #3a0a46 100%);
            min-height: 100vh;
            padding: 24px;
        }

        .page {
            max-width: 700px;
            margin: 0 auto;
        }

        .hero {
            text-align: center;
            margin-bottom: 20px;
        }

        .title {
            font-size: 2.2rem;
            font-weight: 900;
            color: #ffb3e6;
            text-shadow:
                0 0 8px #ff4fc3,
                0 0 16px #ff4fc3,
                0 0 28px rgba(255,79,195,0.75);
            margin-bottom: 8px;
        }

        .subtitle {
            font-size: 1rem;
            color: #ffd7f1;
            opacity: 0.95;
            line-height: 1.5;
        }

        .panel {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,182,230,0.25);
            border-radius: 24px;
            padding: 22px;
            backdrop-filter: blur(10px);
            box-shadow:
                0 0 18px rgba(255, 20, 147, 0.25),
                0 0 40px rgba(255, 105, 180, 0.12);
        }

        .chips {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: center;
            margin-bottom: 18px;
        }

        .chip {
            padding: 8px 14px;
            border-radius: 999px;
            background: rgba(255, 105, 180, 0.15);
            border: 1px solid rgba(255,182,230,0.25);
            color: #ffd7f1;
            font-size: 0.92rem;
        }

        label {
            display: block;
            text-align: left;
            margin: 14px 0 8px;
            font-weight: bold;
            color: #ffd7f1;
        }

        input[type="text"], textarea, input[type="file"] {
            width: 100%;
            border: none;
            border-radius: 14px;
            padding: 14px;
            font-size: 1rem;
        }

        textarea {
            resize: vertical;
            min-height: 110px;
        }

        input[type="text"], textarea {
            background: rgba(255,255,255,0.96);
            color: #2d0033;
        }

        input[type="file"] {
            background: rgba(255,255,255,0.92);
            color: #2d0033;
        }

        .button {
            margin-top: 18px;
            width: 100%;
            border: none;
            border-radius: 16px;
            padding: 15px;
            font-size: 1.05rem;
            font-weight: bold;
            cursor: pointer;
            color: white;
            background: linear-gradient(90deg, #ff4fc3, #ff7bd5, #ff4fc3);
            box-shadow:
                0 0 12px rgba(255,79,195,0.65),
                0 0 28px rgba(255,79,195,0.35);
        }

        .button:hover {
            transform: translateY(-1px);
        }

        .footer-note {
            margin-top: 16px;
            text-align: center;
            color: #ffd7f1;
            font-size: 0.92rem;
            opacity: 0.9;
        }

        .code-line {
            margin-top: 14px;
            text-align: center;
            color: #ffb3e6;
            font-family: Consolas, monospace;
            font-size: 0.95rem;
        }

        @media (max-width: 600px) {
            body {
                padding: 16px;
            }

            .title {
                font-size: 1.8rem;
            }

            .panel {
                padding: 18px;
                border-radius: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="page">
        <div class="hero">
            <div class="title">Upload Your Grad Pics 💕</div>
            <div class="subtitle">
                Help me capture the memories from my graduation party.<br>
                Drop your photos below + leave your name and a sweet message if you want ✨
            </div>
        </div>

        <div class="chips">
            <div class="chip">&lt;/&gt; pink neon mode</div>
            <div class="chip">📸 mobile friendly</div>
            <div class="chip">💖 memory upload portal</div>
        </div>

        <div class="panel">
            <form method="POST" enctype="multipart/form-data">
                <label for="name">Your Name (optional)</label>
                <input type="text" id="name" name="name" placeholder="ex: Connie's favorite cousin">

                <label for="message">Message (optional)</label>
                <textarea id="message" name="message" placeholder="Leave a cute note, joke, or memory 💬"></textarea>

                <label for="photos">Choose Photos</label>
                <input type="file" id="photos" name="photos" multiple required accept="image/*">

                <button class="button" type="submit">Upload Photos 💗</button>
            </form>

            <div class="code-line">def celebrate(): memories += photos</div>
            <div class="footer-note">Thanks for celebrating with me 💕</div>
        </div>
    </div>
</body>
</html>
"""

THANK_YOU_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Uploaded 💖</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            margin: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
            font-family: Arial, sans-serif;
            color: white;
            background:
                radial-gradient(circle at top left, rgba(255,105,180,0.28), transparent 25%),
                radial-gradient(circle at bottom right, rgba(255,20,147,0.22), transparent 25%),
                linear-gradient(135deg, #140014, #250028 40%, #3a0a46 100%);
        }

        .card {
            max-width: 520px;
            width: 100%;
            text-align: center;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,182,230,0.25);
            border-radius: 24px;
            padding: 28px;
            box-shadow:
                0 0 18px rgba(255, 20, 147, 0.25),
                0 0 40px rgba(255, 105, 180, 0.12);
        }

        h1 {
            color: #ffb3e6;
            text-shadow: 0 0 10px #ff4fc3;
            margin-bottom: 12px;
        }

        p {
            color: #ffd7f1;
            line-height: 1.6;
        }

        a {
            display: inline-block;
            margin-top: 16px;
            text-decoration: none;
            color: white;
            background: linear-gradient(90deg, #ff4fc3, #ff7bd5);
            padding: 12px 18px;
            border-radius: 14px;
            font-weight: bold;
            box-shadow: 0 0 14px rgba(255,79,195,0.4);
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>Uploaded! 💖</h1>
        <p>Your photos were sent successfully.<br>Thank you for being part of my special day ✨</p>
        <a href="/">Upload More</a>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        files = request.files.getlist("photos")
        name = request.form.get("name", "").strip()
        message = request.form.get("message", "").strip()

        meta = load_meta()

        for file in files:
            if file and file.filename:
                original_name = secure_filename(file.filename)
                unique_name = f"{uuid.uuid4()}_{original_name}"
                file.save(os.path.join(UPLOAD_FOLDER, unique_name))

                meta.append({
                    "file": unique_name,
                    "original_name": original_name,
                    "name": name,
                    "message": message,
                    "uploaded_at": datetime.now().strftime("%Y-%m-%d %I:%M %p")
                })

        save_meta(meta)
        return THANK_YOU_HTML

    return UPLOAD_HTML


@app.route("/gallery")
def gallery():
    key = request.args.get("key")
    if key != ADMIN_KEY:
        return "Access denied", 403

    meta = load_meta()
    meta = list(reversed(meta))

    cards = []
    for item in meta:
        display_name = item.get("name") or "Anonymous Guest"
        message = item.get("message") or ""
        uploaded_at = item.get("uploaded_at", "")
        filename = item["file"]

        cards.append(f"""
        <div class="card">
            <img src="/uploads/{filename}" alt="{filename}">
            <div class="info">
                <div class="name">{display_name}</div>
                {"<div class='message'>💬 " + message + "</div>" if message else ""}
                <div class="time">{uploaded_at}</div>
            </div>
        </div>
        """)

    gallery_html = "".join(cards) if cards else "<p class='empty'>No uploads yet 💔</p>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gallery 💕</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="refresh" content="20">
        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background:
                    radial-gradient(circle at top left, rgba(255,105,180,0.28), transparent 25%),
                    radial-gradient(circle at bottom right, rgba(255,20,147,0.22), transparent 25%),
                    linear-gradient(135deg, #140014, #250028 40%, #3a0a46 100%);
                color: white;
                padding: 20px;
            }}

            .wrap {{
                max-width: 1200px;
                margin: 0 auto;
            }}

            .header {{
                text-align: center;
                margin-bottom: 24px;
            }}

            .title {{
                font-size: 2.2rem;
                font-weight: 900;
                color: #ffb3e6;
                text-shadow:
                    0 0 8px #ff4fc3,
                    0 0 16px #ff4fc3,
                    0 0 28px rgba(255,79,195,0.75);
            }}

            .sub {{
                margin-top: 8px;
                color: #ffd7f1;
                opacity: 0.92;
            }}

            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                gap: 18px;
            }}

            .card {{
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,182,230,0.22);
                border-radius: 20px;
                overflow: hidden;
                box-shadow:
                    0 0 18px rgba(255, 20, 147, 0.18),
                    0 0 32px rgba(255, 105, 180, 0.08);
            }}

            .card img {{
                display: block;
                width: 100%;
                height: 260px;
                object-fit: cover;
                background: #220022;
            }}

            .info {{
                padding: 14px;
            }}

            .name {{
                font-weight: bold;
                font-size: 1rem;
                color: #ffd7f1;
                margin-bottom: 8px;
            }}

            .message {{
                color: #fff0fa;
                line-height: 1.5;
                margin-bottom: 10px;
                word-wrap: break-word;
            }}

            .time {{
                font-size: 0.86rem;
                color: #ffb3e6;
                opacity: 0.9;
            }}

            .empty {{
                text-align: center;
                color: #ffd7f1;
                font-size: 1.1rem;
                margin-top: 40px;
            }}

            .topbar {{
                display: flex;
                justify-content: center;
                gap: 10px;
                flex-wrap: wrap;
                margin-bottom: 20px;
            }}

            .chip {{
                padding: 8px 14px;
                border-radius: 999px;
                background: rgba(255, 105, 180, 0.15);
                border: 1px solid rgba(255,182,230,0.25);
                color: #ffd7f1;
                font-size: 0.92rem;
            }}

            @media (max-width: 600px) {{
                body {{
                    padding: 14px;
                }}

                .title {{
                    font-size: 1.7rem;
                }}

                .grid {{
                    grid-template-columns: 1fr;
                }}

                .card img {{
                    height: 240px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="wrap">
            <div class="header">
                <div class="title">Grad Party Gallery 💕</div>
                <div class="sub">Auto-refreshing every 20 seconds ✨</div>
            </div>

            <div class="topbar">
                <div class="chip">&lt;/&gt; pink neon gallery</div>
                <div class="chip">📸 live updates</div>
                <div class="chip">💬 guest notes enabled</div>
            </div>

            <div class="grid">
                {gallery_html}
            </div>
        </div>
    </body>
    </html>
    """


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True)