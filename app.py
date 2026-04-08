from flask import Flask, request, render_template_string, send_from_directory
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ADMIN_KEY = "mysecretgallery"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Upload Pics 💖</title>
    <style>
        body {
            font-family: Arial;
            text-align: center;
            background: linear-gradient(135deg, #ffb6c1, #ff69b4);
            color: white;
            padding: 30px;
        }
        .box {
            background: rgba(255,255,255,0.2);
            padding: 20px;
            border-radius: 20px;
            max-width: 400px;
            margin: auto;
        }
        input, button {
            margin: 10px;
            padding: 10px;
            border-radius: 10px;
            border: none;
        }
        button {
            background: hotpink;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }
        img {
            border-radius: 10px;
            margin: 10px;
            max-width: 200px;
            height: auto;
        }
        a {
            color: white;
        }
    </style>
</head>
<body>
    <div class="box">
        <h2>📸 Upload Your Pics!</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="photos" multiple required><br>
            <button type="submit">Upload 💕</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        files = request.files.getlist("photos")

        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                unique_name = f"{uuid.uuid4()}_{filename}"
                file.save(os.path.join(UPLOAD_FOLDER, unique_name))

        return "<h2>Uploaded! 💖</h2><a href='/'>Upload more</a>"

    return render_template_string(HTML)


@app.route("/gallery")
def gallery():
    key = request.args.get("key")
    if key != ADMIN_KEY:
        return "Access denied", 403

    files = os.listdir(UPLOAD_FOLDER)
    image_tags = "".join(
        f"<img src='/uploads/{f}' alt='{f}'>" for f in files
    )

    return f"<h1>Gallery 💕</h1>{image_tags}"


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
    

if __name__ == "__main__":
    app.run(debug=True)