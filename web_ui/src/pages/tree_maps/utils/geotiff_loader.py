import tempfile
import rasterio
import numpy as np
import base64
from PIL import Image
import os

def load_geotiff_bounds_and_url(tiff_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tif") as tmp:
            tmp.write(tiff_file.read())
            tiff_path = tmp.name

        with rasterio.open(tiff_path) as src:
            bounds = [[src.bounds.bottom, src.bounds.left], [src.bounds.top, src.bounds.right]]
            img = src.read([1, 2, 3])  # RGB
            img = np.transpose(img, (1, 2, 0))
            img = np.clip(img, 0, 255).astype(np.uint8)
            pil_img = Image.fromarray(img)
            img_path = tmp.name + ".png"
            pil_img.save(img_path)

        # Генерируем data URL для вставки в Folium
        with open(img_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            url = "data:image/png;base64," + encoded

        return bounds, url
    except Exception as e:
        print(f"Ошибка загрузки GeoTIFF: {e}")
        return None, None