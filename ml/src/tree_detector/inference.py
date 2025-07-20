import rasterio
from rasterio.warp import transform as warp_transform  # Изменено имя импорта
from typing import List, Tuple
from .utils import read_rgb_patch, compute_mask_centroids
from .model import TreeSegmentationService

MAX_SIZE = 2000

def process_geotiff(file_path: str, model: TreeSegmentationService) -> List[Tuple[float, float]]:
    """Обрабатывает GeoTIFF и возвращает геокоординаты центров масок в WGS84."""
    tree_coords = []

    with rasterio.open(file_path) as src:
        src_transform = src.transform  # Переименовано
        src_crs = src.crs
        width, height = src.width, src.height
        bands = src.count

        if src_crs is None:
            raise ValueError("GeoTIFF не содержит информацию о системе координат (CRS)")

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

                src_points = []
                for x_pix, y_pix in pixel_centers:
                    lon, lat = rasterio.transform.xy(src_transform, y_pix, x_pix)  # Исправлено
                    src_points.append((lon, lat))

                if src_points:
                    xs, ys = zip(*src_points)
                    dst_lons, dst_lats = warp_transform(  # Исправлено имя функции
                        src_crs=src_crs,
                        dst_crs="EPSG:4326",
                        xs=xs,
                        ys=ys
                    )
                    tree_coords.extend(zip(dst_lons, dst_lats))

    return tree_coords
