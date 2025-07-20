import rasterio
from typing import List, Tuple
from .utils import read_rgb_patch, compute_mask_centroids
from .model import TreeSegmentationService


MAX_SIZE = 2000


def process_geotiff(file_path: str, model: TreeSegmentationService) -> List[Tuple[float, float]]:
    """Обрабатывает GeoTIFF и возвращает геокоординаты центров масок."""
    tree_coords = []

    with rasterio.open(file_path) as src:
        transform = src.transform
        width, height = src.width, src.height
        bands = src.count

        if bands < 3:
            raise ValueError("GeoTIFF должен содержать хотя бы 3 канала (RGB).")

        x_tiles = list(range(0, width, MAX_SIZE))
        y_tiles = list(range(0, height, MAX_SIZE))

        for y0 in y_tiles:
            for x0 in x_tiles:
                w = min(MAX_SIZE, width - x0)
                h = min(MAX_SIZE, height - y0)
                image_tile = read_rgb_patch(src, x0, y0, w, h)

                outputs = model.predict(image_tile)
                instances = outputs["instances"].to("cpu")

                masks = instances.pred_masks.numpy()
                pixel_centers = compute_mask_centroids(masks, x0, y0)

                for x_pix, y_pix in pixel_centers:
                    lon, lat = rasterio.transform.xy(transform, y_pix, x_pix)
                    tree_coords.append((lon, lat))

    return tree_coords
