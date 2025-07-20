import numpy as np
from rasterio.windows import Window
from rasterio.plot import reshape_as_image


def read_rgb_patch(src, x_off, y_off, w, h):
    """Читает RGB-патч из GeoTIFF."""
    window = Window(x_off, y_off, w, h)
    patch = src.read([1, 2, 3], window=window)
    return reshape_as_image(patch)


def compute_mask_centroids(masks, x_offset: int, y_offset: int):
    """Находит центры масок и возвращает в глобальных координатах."""
    centers = []
    for mask in masks:
        ys, xs = np.where(mask)
        if len(xs) == 0 or len(ys) == 0:
            continue
        x_center = int(np.mean(xs)) + x_offset
        y_center = int(np.mean(ys)) + y_offset
        centers.append((x_center, y_center))
    return centers
