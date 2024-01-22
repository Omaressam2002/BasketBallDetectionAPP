# map data from data model to json
from rest_framework import serializers
from .models import PicPath

class PathSerializer(serializers.ModelSerializer):
    class Meta:
        model = PicPath
        fields = '__all__'