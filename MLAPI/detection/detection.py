import torch
from PIL import Image
from .YOLO_model import YOLOv1
from .utils import save_image
from torchvision import transforms
import numpy as np


class detect:
    def __init__(self):
        model_path = '/Users/omarelshobky/pytorch-test/MLAPI/MLAPI/YOLOv1.pth'
        self.model = YOLOv1()
        self.model.load_state_dict(torch.load(model_path)["state_dict"])
        self.model.eval()

    def predict(self,src_path):
        img = Image.open(src_path)
        image_size = np.array(img).shape
        img = transforms.Resize((448, 448))(img)
        img = transforms.ToTensor()(img)
        # outputs list of boxes 
        bboxes = self.model.predict(img)
        dest_path = save_image(bboxes,src_path)

        return dest_path