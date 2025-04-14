from pathlib import Path
from PIL import Image
from app.overlay import render_video_overlay, apply_stencil, TEMPLATE_SIZE, STATIC_DIR


def test_video_overlay_html_generation(tmp_path):
    dummy_video = tmp_path / "test_video.mp4"
    dummy_video.write_bytes(b"fake mp4 data")

    html = render_video_overlay(dummy_video)

    static_file = Path(STATIC_DIR) / dummy_video.name
    assert static_file.exists(), "Video should be copied to static directory"
    assert dummy_video.name in html, "HTML should reference the copied video"
    assert "<video" in html and "<img" in html, "HTML should contain both video and mask tags"

    static_file.unlink(missing_ok=True)


def test_apply_stencil_on_valid_image():
    image = Image.new("RGB", (800, 600), color="green")
    result = apply_stencil(image)

    assert result is not None
    assert isinstance(result, Image.Image)
    assert result.size == TEMPLATE_SIZE
    assert result.mode == "RGBA"
