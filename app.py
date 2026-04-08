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


UPLOAD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Upload Your Grad Pics 💕</title>
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


@app.route("/slideshow")
def slideshow():
    key = request.args.get("key")
    if key != ADMIN_KEY:
        return "Access denied", 403

    meta = list(reversed(load_meta()))

    slides = []
    for item in meta:
        slides.append({
            "img": f"/uploads/{item['file']}",
            "name": item.get("name") or "Guest",
            "msg": item.get("message") or ""
        })

    first = slides[0] if slides else {"img": "", "name": "", "msg": ""}

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="30">
    <title>Slideshow 💕</title>
    <style>
        body {{
            margin: 0;
            background:
                radial-gradient(circle at top left, rgba(255,105,180,0.22), transparent 25%),
                radial-gradient(circle at bottom right, rgba(255,20,147,0.16), transparent 25%),
                linear-gradient(135deg, #120014, #24002c, #390047);
            font-family: Arial, sans-serif;
            overflow: hidden;
            color: white;
        }}

        .sparkle {{
            position: absolute;
            width: 6px;
            height: 6px;
            background: white;
            border-radius: 50%;
            box-shadow: 0 0 10px white, 0 0 20px hotpink;
            opacity: 0.8;
            animation: twinkle 3s infinite ease-in-out;
        }}

        .sparkle:nth-child(1) {{ top: 10%; left: 12%; animation-delay: 0s; }}
        .sparkle:nth-child(2) {{ top: 20%; left: 80%; animation-delay: 1s; }}
        .sparkle:nth-child(3) {{ top: 75%; left: 15%; animation-delay: 2s; }}
        .sparkle:nth-child(4) {{ top: 65%; left: 88%; animation-delay: 0.5s; }}
        .sparkle:nth-child(5) {{ top: 45%; left: 7%; animation-delay: 1.5s; }}
        .sparkle:nth-child(6) {{ top: 8%; left: 55%; animation-delay: 2.5s; }}
        .sparkle:nth-child(7) {{ top: 85%; left: 60%; animation-delay: 1.2s; }}
        .sparkle:nth-child(8) {{ top: 30%; left: 35%; animation-delay: 0.8s; }}

        @keyframes twinkle {{
            0%, 100% {{ transform: scale(0.7); opacity: 0.3; }}
            50% {{ transform: scale(1.4); opacity: 1; }}
        }}

        .confetti {{
            position: absolute;
            top: -20px;
            width: 10px;
            height: 16px;
            opacity: 0.75;
            animation: fall linear infinite;
        }}

        .confetti:nth-child(9)  {{ left: 5%;  background: #ff69b4; animation-duration: 9s; }}
        .confetti:nth-child(10) {{ left: 15%; background: #ffd1f4; animation-duration: 7s; }}
        .confetti:nth-child(11) {{ left: 28%; background: #ffb6e6; animation-duration: 10s; }}
        .confetti:nth-child(12) {{ left: 42%; background: #ffffff; animation-duration: 8s; }}
        .confetti:nth-child(13) {{ left: 57%; background: #ff8fd8; animation-duration: 11s; }}
        .confetti:nth-child(14) {{ left: 70%; background: #ffc3eb; animation-duration: 7.5s; }}
        .confetti:nth-child(15) {{ left: 83%; background: #ff4fc3; animation-duration: 9.5s; }}
        .confetti:nth-child(16) {{ left: 93%; background: #ffffff; animation-duration: 8.5s; }}

        @keyframes fall {{
            0% {{
                transform: translateY(-20px) rotate(0deg);
                opacity: 0;
            }}
            10% {{
                opacity: 0.85;
            }}
            100% {{
                transform: translateY(110vh) rotate(360deg);
                opacity: 0;
            }}
        }}

        .wrap {{
            position: relative;
            width: 100vw;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }}

        .story-frame {{
            position: relative;
            width: min(92vw, 520px);
            height: min(88vh, 920px);
            border-radius: 34px;
            overflow: hidden;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            box-shadow:
                0 0 25px rgba(255,20,147,0.35),
                0 0 70px rgba(255,105,180,0.18);
            backdrop-filter: blur(8px);
        }}

        .top-ui {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 5;
            padding: 18px 18px 0 18px;
        }}

        .progress {{
            width: 100%;
            height: 4px;
            background: rgba(255,255,255,0.22);
            border-radius: 999px;
            overflow: hidden;
            margin-bottom: 14px;
        }}

        .progress-bar {{
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, #ffb6e6, #ff4fc3, #ffffff);
            transform-origin: left;
            animation: progress 10s linear infinite;
        }}

        @keyframes progress {{
            0% {{ transform: scaleX(0); }}
            100% {{ transform: scaleX(1); }}
        }}

        .story-badge {{
            display: inline-block;
            background: rgba(0,0,0,0.35);
            color: #ffd9f5;
            border: 1px solid rgba(255,255,255,0.16);
            border-radius: 999px;
            padding: 10px 16px;
            font-size: 0.95rem;
            font-weight: bold;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 18px rgba(255,79,195,0.2);
        }}

        .slide-img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            opacity: 1;
            transition: opacity 1s ease-in-out;
            background: #1e0022;
        }}

        .gradient-overlay {{
            position: absolute;
            inset: 0;
            background:
                linear-gradient(to bottom, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0.05) 35%, rgba(0,0,0,0.55) 100%);
            pointer-events: none;
        }}

        .bottom-card {{
            position: absolute;
            left: 18px;
            right: 18px;
            bottom: 20px;
            z-index: 5;
            background: rgba(10, 0, 18, 0.45);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 24px;
            padding: 16px 18px;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 20px rgba(255,79,195,0.18);
        }}

        .name {{
            font-size: 1.05rem;
            font-weight: bold;
            color: #ffe3f8;
            margin-bottom: 8px;
            text-shadow: 0 0 8px rgba(255,79,195,0.45);
        }}

        .msg {{
            font-size: 0.98rem;
            line-height: 1.5;
            color: #fff4fc;
            word-wrap: break-word;
        }}

        .corner-glow {{
            position: absolute;
            width: 180px;
            height: 180px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255,79,195,0.25), transparent 70%);
            filter: blur(14px);
            pointer-events: none;
            z-index: 1;
        }}

        .corner-glow.one {{
            top: -50px;
            left: -50px;
        }}

        .corner-glow.two {{
            bottom: -60px;
            right: -60px;
        }}

        @media (max-width: 700px) {{
            .story-frame {{
                width: 95vw;
                height: 88vh;
                border-radius: 26px;
            }}

            .bottom-card {{
                left: 12px;
                right: 12px;
                bottom: 14px;
                border-radius: 20px;
                padding: 14px;
            }}

            .name {{
                font-size: 1rem;
            }}

            .msg {{
                font-size: 0.92rem;
            }}
        }}
    </style>
    </head>
    <body>

        <div class="sparkle"></div>
        <div class="sparkle"></div>
        <div class="sparkle"></div>
        <div class="sparkle"></div>
        <div class="sparkle"></div>
        <div class="sparkle"></div>
        <div class="sparkle"></div>
        <div class="sparkle"></div>

        <div class="confetti"></div>
        <div class="confetti"></div>
        <div class="confetti"></div>
        <div class="confetti"></div>
        <div class="confetti"></div>
        <div class="confetti"></div>
        <div class="confetti"></div>
        <div class="confetti"></div>

        <div class="wrap">
            <div class="story-frame">
                <div class="corner-glow one"></div>
                <div class="corner-glow two"></div>

                <div class="top-ui">
                    <div class="progress">
                        <div class="progress-bar" id="progress-bar"></div>
                    </div>
                    <div class="story-badge">Grad Party Memories 💕</div>
                </div>

                <img id="slide" class="slide-img" src="{first['img']}">
                <div class="gradient-overlay"></div>

                <div class="bottom-card">
                    <div class="name" id="name">{first['name']}</div>
                    <div class="msg" id="msg">{first['msg']}</div>
                </div>
            </div>
        </div>

        <script>
            const slides = {json.dumps(slides)};
            let i = 0;

            const img = document.getElementById("slide");
            const name = document.getElementById("name");
            const msg = document.getElementById("msg");
            const progressBar = document.getElementById("progress-bar");

            function restartProgress() {{
                progressBar.style.animation = "none";
                progressBar.offsetHeight;
                progressBar.style.animation = "progress 10s linear infinite";
            }}

            setInterval(() => {{
                if (slides.length === 0) return;

                img.style.opacity = 0;

                setTimeout(() => {{
                    i = (i + 1) % slides.length;
                    img.src = slides[i].img;
                    name.textContent = slides[i].name;
                    msg.textContent = slides[i].msg;
                    img.style.opacity = 1;
                    restartProgress();
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