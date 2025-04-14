from PIL import Image, ImageOps
from pathlib import Path
import shutil

TEMPLATE_SIZE = (1080, 1920)
STATIC_DIR = "static"
STENCIL_FILENAME = "stencil_1080x1920.png"
STENCIL_PATH = Path(STATIC_DIR) / STENCIL_FILENAME

stencil = Image.open(STENCIL_PATH).convert("RGBA")


def apply_stencil(image: Image.Image) -> Image.Image | None:
    if image is None:
        return None

    image = image.convert("RGBA")
    image = ImageOps.fit(image, TEMPLATE_SIZE, method=Image.BICUBIC, centering=(0.5, 0.5))
    return Image.alpha_composite(image, stencil)


def render_video_overlay(video_file: Path) -> str:
    target_path = Path(STATIC_DIR) / video_file.name
    shutil.copyfile(video_file, target_path)

    return f"""
    <div style='position: relative; width: 100%; max-width: 360px;'>
        <video src='{target_path.as_posix()}' autoplay muted controls style='width: 100%; height: auto;'></video>
        <img src='{STENCIL_PATH.as_posix()}' style='position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;'>
    </div>
    """