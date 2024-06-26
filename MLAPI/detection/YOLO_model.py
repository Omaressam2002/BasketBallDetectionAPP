import torch
import torch.nn as nn
from .utils import non_max_suppression,parse_predictions
from .operators import ConvBlock,GlobalAvgPool2d


class darkNet(nn.Module): #Architectures
    def __init__(self,classes=1000):
        super(darkNet, self).__init__()
        self.darkNet = nn.Sequential(
             ConvBlock(7,3,64,2,3),
             nn.MaxPool2d(kernel_size=2,stride=2),
             ConvBlock(3,64,192,padding=1),
             nn.MaxPool2d(kernel_size=2,stride=2),
             ConvBlock(1,192,128),
             ConvBlock(3,128,256,padding=1),
             ConvBlock(1,256,256),
             ConvBlock(3,256,512,padding=1),
             nn.MaxPool2d(kernel_size=2,stride=2),
             
            ConvBlock(1,512,256),
            ConvBlock(3,256,512,padding=1),
            ConvBlock(1,512,256),
            ConvBlock(3,256,512,padding=1),
            ConvBlock(1,512,256),
            ConvBlock(3,256,512,padding=1),
            ConvBlock(1,512,256),
            ConvBlock(3,256,512,padding=1),

            ConvBlock(1,512,512),
            ConvBlock(3,512,1024,padding=1),
            nn.MaxPool2d(kernel_size=2,stride=2),

            ConvBlock(1,1024,512),
            ConvBlock(3,512,1024,padding=1),
            ConvBlock(1,1024,512),
            ConvBlock(3,512,1024,padding=1)
        )
        self.classifier = nn.Sequential(
            *self.darkNet,
            GlobalAvgPool2d(),
            nn.Linear(1024, classes)
        )


    def forward(self, x):
        return self.classifier(x)

class YOLOv1(nn.Module): # Architectures
    def __init__(self,grids=7,boxes=2,classes=3):
        super(YOLOv1,self).__init__()
        self.G = grids
        self.B = boxes
        self.C = classes
        self.DN = darkNet().darkNet
        self.fullyConnected = nn.Sequential(
            ConvBlock(3,1024,1024,padding=1),
            ConvBlock(3,1024,1024,stride=2,padding=1),
            
            ConvBlock(3,1024,1024,padding=1),
            ConvBlock(3,1024,1024,padding=1),

            nn.Flatten(),
            nn.Linear(grids*grids*1024, 1024),
            nn.LeakyReLU(0.1),
            nn.Dropout(p=0.5),
            nn.Linear(1024, grids*grids*(classes+ boxes*5))
        )
    def forward(self,x):
        x = self.DN(x)
        out = self.fullyConnected(x)
        out = out.reshape(-1,self.G,self.G,self.C+(5*self.B))
        return out

    def predict(self,x):
        # to make sure x is one pic not a batch
        assert len(x.shape) == 3
        x = x.unsqueeze(0)
        with torch.no_grad():
            pred = self.forward(x)
            #for each grid [0->3 for class prob, obj, x,y,w,h, obj, x,y,w,h]
        
        pred = parse_predictions(pred)# shape 49,6
        # for each grid [class_idx,best_conf,x,y,w,h] dims for the box of the best confidence
        pred = non_max_suppression(pred,iou_threshold=0.1,prob_threshold= 0.3)

        # pred is final output boxes
        return pred