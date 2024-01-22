from django.http import JsonResponse
from .models import PicPath
from .serializers import PathSerializer
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from .detection.detection import detect


@api_view(['POST'])
def path_list(request):
    if request.method == 'POST':
        # YoloV1 model
        model = detect()
        img_path = None
        
        # converts the request data to json
        serializer = PathSerializer(data = request.data)
        if serializer.is_valid():
            img_path = (serializer.data)["src_path"]
            # to convert from the swift-app url format
            if "file://" in img_path:
                img_path2 = img_path[7:].replace("%20", " ")
                
        if img_path is None:
            return Response("invalid body", status=status.HTTP_404_NOT_FOUND)
        else:
            # predict and save the pred image next to the original
            # and return the destination path
            dest_path = model.predict(img_path2)
            # use the swift-app path and send it back thru the api
            p = img_path.split(".jpg")
            dest_path2 = p[0]+"_predicted.jpg"
            resp = {
                "id":0,
                "src_path":dest_path2
            }
            return Response(resp, status=status.HTTP_201_CREATED)