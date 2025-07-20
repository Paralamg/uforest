
from src.tree_detector.model import TreeSegmentationService
from src.tree_detector.inference import process_geotiff

def read_local_geotiff(file_path: str) -> bytes:
    """Чтение GeoTIFF файла с диска в виде байтов"""
    with open(file_path, "rb") as f:
        return f.read()

# Загрузка модели
model = TreeSegmentationService(model_dir="models/rcnn_R_101")

# Локальный путь к файлу
file_path = "examples/68762df522caa22a41b139a5.tif"

# Чтение файла
geotiff_bytes = read_local_geotiff(file_path)

# Обработка файла
coords = process_geotiff(geotiff_bytes, model)

print(f"Найдено деревьев: {len(coords)}")
print("Координаты деревьев:")
for i, (lon, lat) in enumerate(coords, 1):
    print(f"{i}: ({lon:.6f}, {lat:.6f})")