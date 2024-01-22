import torch
import numpy as np
import cv2

def parse_predictions(predictions): #Utils
    #[0,1,0,0,0,..,obj,x_cell,y_cell,w_cell,h_cell] -> [class label,obj_conf,x_global,y_global,w_global,h_global]
    #for each grid

    g=7
    c=3

    predictions = predictions.to("cpu")
    batch = predictions.shape[0]
    
    bboxes1 = predictions[..., c+1:c+5]
    bboxes2 = predictions[..., c+6:c+10]
    #confidence in each anchor box
    scores = torch.cat(
        (predictions[..., c].unsqueeze(0), predictions[..., c+5].unsqueeze(0)), dim=0
    )

    best_confidence,best_box= torch.max(scores,dim=0)

    best_box = best_box.unsqueeze(-1)
    bboxes = (1-best_box) * bboxes1 + best_box * bboxes2

    #globalizing the coordinates
    #
    cell_no = torch.arange(g).repeat(batch,g,1).unsqueeze(-1)
    x = 1/g * (bboxes[...,0:1]+cell_no)
    y = 1/g * (bboxes[...,1:2]+cell_no.permute(0,2,1,3))
    w_h = 1/g * bboxes[...,2:4]

    bboxes = torch.cat((x,y,w_h),dim=-1)

    class_labels = predictions[...,0:c].argmax(-1).unsqueeze(-1)
    best_confidence = best_confidence.unsqueeze(-1)

    preds_parsed = torch.cat((class_labels,best_confidence,bboxes),dim=-1).reshape(batch,g*g,6) 

    converted_predictions = []
    for i in range(batch):
        picture =[]
        for j in range(g*g):
            picture.append([x.item() for x in preds_parsed[i,j,:]])
        converted_predictions.append(picture)
    return converted_predictions 


def non_max_suppression(prediction,iou_threshold,prob_threshold): #Utils
    
    nms_boxes = []

    prediction = prediction[0] #1,49,6 -> 49,6
    
    prediction = [box for box in prediction if box[1] > 
    prob_threshold]
    
    prediction = sorted(prediction, key=lambda x: x[1], reverse=True) # sort based on prob threshold

    while prediction:
        box = prediction.pop(0)
        # get most confident box and remove other boxes that over lap with it
    

        prediction = [b for b in prediction if (b[0] != box[0] or iou(torch.Tensor(b[2:]),torch.Tensor(box[2:])) < iou_threshold)]

        
        nms_boxes.append(box)

    return nms_boxes 


 

def save_image(boxes,src_path):
    cv2.ocl.setUseOpenCL(False)
    im = cv2.imread(src_path)
    width, height, _ = im.shape
    

    #            r    ,    g    ,    b
    colors =[(0,0,255),(0,255,0),(255,0,0)]

    for box in boxes:
        c = colors[int(box[0])]
        conf = box[1]
        box = box[2:]
        x = int((box[0] - box[2] / 2)*width)
        y = int((box[1] - box[3] / 2)*height)
        w = int(box[2] * width)
        h = int(box[3] * height)

        im = cv2.rectangle(im, (x, y), (x+w, y+h),c, 2)
        im = cv2.putText(im, str(conf)[:4], (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
    

    dest_path = src_path[:-4]+"_predicted.jpg"
    cv2.imwrite(dest_path,im)
    return dest_path


def iou(box1, box2,format="midpoint"):
    if format == "midpoint":
        box1_x = box1[...,0:1]
        box1_y = box1[...,1:2]
        box1_w = box1[...,2:3]
        box1_h = box1[...,3:4]
        box2_x = box2[...,0:1]
        box2_y = box2[...,1:2]
        box2_w = box2[...,2:3]
        box2_h = box2[...,3:4]

        box1 = midToCorners(torch.cat((box1_x,box1_y,box1_w,box1_h),dim=-1))
        box2 = midToCorners(torch.cat((box2_x,box2_y,box2_w,box2_h),dim=-1))

        box1_x1 = box1[...,0:1]
        box1_y1 = box1[...,1:2]
        box1_x2 = box1[...,2:3]
        box1_y2 = box1[...,3:4]
        box2_x1 = box2[...,0:1]
        box2_y1 = box2[...,1:2]
        box2_x2 = box2[...,2:3]
        box2_y2 = box2[...,3:4]

        # box1_x1 = torch.sub(box1_x,box1_w,alpha=0.5) #box1_x-(box1_w/2)
        # box1_y1 = torch.sub(box1_y,box1_h,alpha=0.5) #box1_y-(box1_h/2)
        # box1_x2 = torch.add(box1_x,box1_w,alpha=0.5) #box1_x+(box1_w/2)
        # box1_y2 = torch.add(box1_y,box1_h,alpha=0.5) #box1_y+(box1_h/2)
        # box2_x1 = torch.sub(box2_x,box2_w,alpha=0.5) #box2_x-(box2_w/2)
        # box2_y1 = torch.sub(box2_y,box2_h,alpha=0.5) #box2_y-(box2_h/2)
        # box2_x2 = torch.add(box2_x,box2_w,alpha=0.5) #box2_x+(box2_w/2)
        # box2_y2 = torch.add(box2_y,box2_h,alpha=0.5) #box2_y+(box2_h/2)

        
    
    elif format == "corners":
        box1_x1 = box1[...,0:1]
        box1_y1 = box1[...,1:2]
        box1_x2 = box1[...,2:3]
        box1_y2 = box1[...,3:4]
        box2_x1 = box2[...,0:1]
        box2_y1 = box2[...,1:2]
        box2_x2 = box2[...,2:3]
        box2_y2 = box2[...,3:4]
        

    
    xi1 = torch.max(box1_x1,box2_x1)
    yi1 = torch.max(box1_y1,box2_y1)
    xi2 = torch.min(box1_x2,box2_x2)
    yi2 = torch.min(box1_y2,box2_y2)


    
    inter_width = torch.clamp(yi2-yi1 , min=0) 
    inter_height = torch.clamp(xi2-xi1 , min=0)
    inter_area = inter_width*inter_height

    box1_area = torch.mul(torch.sub(box1_x2,box1_x1),torch.sub(box1_y2,box1_y1))
    box2_area = torch.mul(torch.sub(box2_x2,box2_x1),torch.sub(box2_y2,box2_y1))
    union_area = box1_area + box2_area - inter_area

    iou = inter_area/union_area
    return iou


def midToCorners(box): 
    #[x,y,w,h]
    assert type(box) == torch.Tensor
    
    x1 = torch.sub(box[...,0:1],box[...,2:3],alpha=0.5) #x-(w/2)
    y1 = torch.sub(box[...,1:2],box[...,3:4],alpha=0.5) #y-(h/2)
    x2 = torch.add(box[...,0:1],box[...,2:3],alpha=0.5) #x+(w/2)
    y2 = torch.add(box[...,1:2],box[...,3:4],alpha=0.5) #y+(h/2)
    return torch.cat((x1,y1,x2,y2),dim=-1)