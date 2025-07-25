import base64
from io import BytesIO

from utils.syntax_highlighter_style import SyntaxHighlighterStyle
from PIL import Image
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import ImageFormatter


def code_to_image_base64(code_text, code_ext):
    try:
        lexer = get_lexer_by_name(code_ext, stripall=True)
    except:
        lexer = get_lexer_by_name("text", stripall=True)
        
    font_name = get_preffered_font()

    formatter = ImageFormatter(
        font_name=font_name,
        font_size=30,
        line_numbers=True,
        line_number_bg="#f0f0f0",
        line_number_fg="#999999",
        line_number_pad=18,
        image_pad=6,
        line_pad=10,
        antialias=True,
        dpi=300,
        style=SyntaxHighlighterStyle
    )

    # Render the code as an image
    img_data = highlight(code_text, lexer, formatter)

    # Open the image with PIL
    image = Image.open(BytesIO(img_data))

    # Add padding to the right side
    extra_padding = 380  # You can adjust this
    new_width = image.width + extra_padding
    new_height = image.height

    # Create a new image with background color
    background_color = "#ffffff"  # Or match your background: "#f8f8f8"
    padded_image = Image.new("RGB", (new_width, new_height), background_color)
    padded_image.paste(image, (0, 0))  # Paste original image at top-left

    # Convert padded image to base64
    buffered = BytesIO()
    padded_image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return f"data:image/png;base64,{img_base64}"

def get_preffered_font():
    # Try to use a good-looking cross-platform font
    preferred_fonts = ['Consolas', 'Menlo', 'DejaVu Sans Mono', 'Courier New', 'Monospace']
    font_name = None

    # PIL doesn't offer a direct way to check for installed fonts, so just pick first
    for font in preferred_fonts:
        try:
            formatter = ImageFormatter(font_name=font)
            font_name = font
            break
        except:
            continue

    # Fallback to Courier if nothing worked
    if font_name is None:
        font_name = 'Courier New'

    return font_name