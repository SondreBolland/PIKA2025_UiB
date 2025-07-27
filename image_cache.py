import os
import base64
from utils.code_to_image import code_to_image_bytes

in_memory_images = {}

def preload_images():
    folder = 'static/code_images'
    print(os.listdir(folder), flush=True)
    for fname in os.listdir(folder):
        if fname.endswith('.png'):
            with open(os.path.join(folder, fname), 'rb') as f:
                img_bytes = f.read()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                in_memory_images[fname] = f"data:image/png;base64,{img_b64}"
    print(f"Preloaded {len(in_memory_images)} images into memory.")


def cached_code_to_image_path(code_file, root):
    code_file_path = os.path.join('./config', code_file)
    filename = os.path.basename(code_file)
    image_name = f"{filename}.png"
    image_path = os.path.join('./static/code_images', image_name)

    if not os.path.exists(image_path):
        print("did not find")
        # Render and save image to disk
        with open(code_file_path, 'r', encoding='utf-8') as f:
            code_text = f.read()
        img_data = code_to_image_bytes(code_text, code_file.split('.')[-1])
        with open(image_path, 'wb') as out:
            out.write(img_data)
    if root:
        return f"/{root}/static/code_images/{image_name}"
    return f"/static/code_images/{image_name}"