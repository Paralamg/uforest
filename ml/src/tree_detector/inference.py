import rasterio
from rasterio.warp import transform as warp_transform  # Изменено имя импорта
from rasterio.io import MemoryFile
import numpy as np
from typing import List, Tuple
from .utils import read_rgb_patch, compute_mask_centroids
from .model import TreeSegmentationService

MAX_SIZE = 2000


def process_geotiff(geotiff_bytes: bytes, model: TreeSegmentationService) -> List[Tuple[float, float]]:
    """Обрабатывает GeoTIFF из байтов и возвращает геокоординаты центров масок."""
    tree_coords = []

    with MemoryFile(geotiff_bytes) as memfile:
        with memfile.open() as src:
            src_transform = src.transform
            src_crs = src.crs
            width, height = src.width, src.height
            bands = src.count

            if src_crs is None:
                raise ValueError("GeoTIFF не содержит CRS")
            if bands < 3:
                raise ValueError("Требуется минимум 3 RGB-канала")

            for y0 in range(0, height, MAX_SIZE):
                for x0 in range(0, width, MAX_SIZE):
                    w = min(MAX_SIZE, width - x0)
                    h = min(MAX_SIZE, height - y0)
                    
                    # Чтение RGB-тайла
                    window = ((y0, y0 + h), (x0, x0 + w))
                    tile = src.read([1, 2, 3], window=window)
                    image_tile = np.transpose(tile, (1, 2, 0))
                    
                    # Предсказание и обработка результатов
                    outputs = model.predict(image_tile)
                    instances = outputs["instances"].to("cpu")
                    masks = instances.pred_masks.numpy()
                    
                    for mask in masks:
                        y_indices, x_indices = np.where(mask)
                        if len(y_indices) == 0:
                            continue
                            
                        # Абсолютные координаты центра маски
                        x_abs = x0 + np.mean(x_indices)
                        y_abs = y0 + np.mean(y_indices)
                        
                        # Преобразование в геокоординаты
                        lon, lat = rasterio.transform.xy(src_transform, y_abs, x_abs)
                        xs, ys = warp_transform(
                            src_crs=src_crs,
                            dst_crs="EPSG:4326",
                            xs=[lon],
                            ys=[lat]
                        )
                        tree_coords.append((xs[0], ys[0]))

    return tree_coords
