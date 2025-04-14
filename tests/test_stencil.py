import pytest
from PIL import Image
from app import apply_stencil, TEMPLATE_SIZE

IMG_PATH = "tests/img/4.png"


def test_apply_stencil_valid_image():
    image = Image.open(IMG_PATH)
    result = apply_stencil(image)

    assert result is not None
    assert isinstance(result, Image.Image)
    assert result.size == TEMPLATE_SIZE
    assert result.mode == "RGBA"


def test_apply_stencil_none():
    result = apply_stencil(None)
    assert result is None
