import gradio as gr
from PIL import Image, ImageOps

TEMPLATE_SIZE = (1080, 1920)
STENCIL_PATH = "stencil_1080x1920.png"

stencil = Image.open(STENCIL_PATH).convert("RGBA")


def apply_stencil(image: Image.Image) -> Image.Image | None:
    if image is None:
        return None

    image = image.convert("RGBA")
    image = ImageOps.fit(
        image,
        TEMPLATE_SIZE,
        method=Image.BICUBIC,
        centering=(0.5, 0.5),
    )
    return Image.alpha_composite(image, stencil)


def build_interface() -> gr.Blocks:
    with gr.Blocks() as demo:
        gr.Markdown("# Format Alignment for Instagram Reels/Stories (9:16)")

        with gr.Row():
            input_image = gr.Image(
                type="pil",
                label="Upload Image",
                show_label=True,
                elem_id="input",
            )

            output_image = gr.Image(
                label="Preview with Stencil",
                show_label=True,
                elem_id="output",
            )

        input_image.change(
            fn=apply_stencil,
            inputs=input_image,
            outputs=output_image,
        )

    return demo


if __name__ == "__main__":
    build_interface().launch()
