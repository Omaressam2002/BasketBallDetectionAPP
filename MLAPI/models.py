from django.db import models

# define Database models
class PicPath(models.Model):
    src_path = models.CharField(max_length=200)
    def __str__(self):
        return self.src_path.split('/')[-1]