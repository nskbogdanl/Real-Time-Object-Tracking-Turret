import ultralytics
from roboflow import Roboflow
from pathlib import Path
from ultralytics import YOLO
from IPython.display import Image

DATASET_DIR = Path.home() / "Dataset"

ultralytics.checks()


rf = Roboflow(api_key="kw9NszGfjBZkD9SzsjNU")
project = rf.workspace("nskbogdanl-official").project("santa-ue4mc-pt5rf")
version = project.version(7)
dataset = version.download("yolo26", location=str(DATASET_DIR))

data_path = Path(dataset.location) / "data.yaml"

model = YOLO("yolo26m.pt")
model.train(data=str(data_path), project=str(Path.home() / "runs"), 
            batch=32, workers=8, name="santa", model="yolo26m.pt", epochs=300, imgsz=640, patience=50,
            scale=0.5, degrees=5, translate=0.1, hsv_h=0.01, hsv_s=0.35, hsv_v=0.1,
            mosaic=0.5, copy_paste=0.1, close_mosaic = 30, cache=False)
