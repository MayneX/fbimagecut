from flask_overlay_app import app, TEMPLATE_SIZE, STATIC_DIR, STENCIL_FILENAME
from bs4 import BeautifulSoup
from PIL import Image


def test_index_contains_dropzone():
    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200

        soup = BeautifulSoup(response.data, "html.parser")

        dropzone = soup.find("div", id="dropzone")
        assert dropzone is not None, "Dropzone should be present"

        file_input = soup.find("input", {"type": "file"})
        assert file_input is not None, "File input should be present"

        script_tags = soup.find_all("script")
        assert any("fetch(\"/upload\"" in s.text for s in script_tags), "Upload handler should be defined in JS"


def test_image_processing_logic():
    image = Image.new("RGB", (800, 600), color="blue")
    result = image.convert("RGBA").resize(TEMPLATE_SIZE)
    assert result.size == TEMPLATE_SIZE
    assert result.mode == "RGBA"


def test_static_paths_exist():
    assert STATIC_DIR.exists(), "Static directory should exist"
    assert (STATIC_DIR / STENCIL_FILENAME).exists(), "Stencil not found in static directory"
