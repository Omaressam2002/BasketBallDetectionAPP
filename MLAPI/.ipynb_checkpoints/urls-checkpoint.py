from django.contrib import admin
from django.urls import path
from . import views

#urls and their paths
urlpatterns = [
    path('admin/', admin.site.urls),
    path('paths/', views.path_list)
]
