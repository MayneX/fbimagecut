from flask import Flask, render_template, request, url_for, jsonify
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
from pathlib import Path
import logging
import os
import time
import threading


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static"
TEMPLATE_SIZE = (1080, 1920)
STATIC_DIR = Path(app.config["UPLOAD_FOLDER"])
STENCIL_FILENAME = "stencil_1080x1920.png"
STENCIL_PATH = STATIC_DIR / STENCIL_FILENAME

EXPIRATION_SECONDS = 15 * 60  # 15 minutes
CLEANUP_INTERVAL = 5 * 60     # run cleanup every 5 minutes


def background_cleanup():
    while True:
        now = time.time()
        for file in STATIC_DIR.iterdir():
            try:
                if file.resolve() == STENCIL_PATH.resolve():
                    continue
                if file.is_file() and (now - file.stat().st_mtime > EXPIRATION_SECONDS):
                    file.unlink()
                    logger.info("[CLEANUP] Deleted expired file: %s", file.name)
            except Exception as e:
                logger.warning("[CLEANUP] Failed to delete file: %s", file.name)
        time.sleep(CLEANUP_INTERVAL)


@app.route("/")
def index():
    return render_template("index.html", stencil_url=STENCIL_FILENAME)


@app.route("/upload", methods=["POST"])
def upload():
    stencil = Image.open(STENCIL_PATH).convert("RGBA")

    file = request.files.get("file")
    if not file or not file.filename:
        logger.warning("Empty file upload")
        return jsonify({"error": "No file received"}), 400

    filename = secure_filename(file.filename)
    file_ext = Path(filename).suffix.lower()

    try:
        if file_ext in [".jpg", ".jpeg", ".png"]:
            image = Image.open(file.stream).convert("RGBA")
            image = ImageOps.fit(image, TEMPLATE_SIZE, method=Image.BICUBIC, centering=(0.5, 0.5))
            result = Image.alpha_composite(image, stencil)
            output_filename = f"output_{filename}"
            output_path = STATIC_DIR / output_filename
            result.save(output_path)
            logger.info("Processed image: %s", filename)
            return jsonify({
                "type": "image",
                "url": url_for("static", filename=output_path.name),
                "stencil": url_for("static", filename=STENCIL_FILENAME),
            })

        elif file_ext == ".mp4":
            save_path = STATIC_DIR / filename
            file.save(save_path)
            logger.info("Saved video: %s", filename)
            return jsonify({
                "type": "video",
                "url": url_for("static", filename=filename),
                "stencil": url_for("static", filename=STENCIL_FILENAME),
            })

        else:
            logger.warning("Unsupported file type: %s", filename)
            return jsonify({"error": "Unsupported file type"}), 400

    except Exception as e:
        logger.exception("Failed to handle file upload")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    os.makedirs(STATIC_DIR, exist_ok=True)
    threading.Thread(target=background_cleanup, daemon=True).start()
    app.run(debug=True)