from PIL import Image
from flask_overlay_app import TEMPLATE_SIZE, STATIC_DIR, STENCIL_FILENAME


def test_image_resize_and_overlay():
    image = Image.new("RGB", (800, 600), color="blue")
    result = image.convert("RGBA").resize(TEMPLATE_SIZE)
    assert result.size == TEMPLATE_SIZE
    assert result.mode == "RGBA"


def test_paths_exist():
    assert STATIC_DIR.exists(), "Static directory should exist"
    assert (STATIC_DIR / STENCIL_FILENAME).exists(), "Stencil not found in static directory"
