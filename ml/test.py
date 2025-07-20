from src.tree_detector.model import TreeSegmentationService
from src.tree_detector.inference import process_geotiff

model = TreeSegmentationService(model_dir="models/rcnn_R_101")
coords = process_geotiff("examples/68762df522caa22a41b139a5.tif", model)

print("Координаты деревьев:")
for i, (lon, lat) in enumerate(coords, 1):
    print(f"{i}: ({lon:.6f}, {lat:.6f})")
