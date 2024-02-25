from django.db import models
from django.contrib.auth import get_user_model

import os 

user_model = get_user_model()

def get_file_path(instance, filename):
        return f"images/user_{instance.user.username}/{filename}"

class Image(models.Model):
    image = models.ImageField(upload_to=get_file_path)
    user = models.ForeignKey(user_model, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        userd_dir = os.path.join("images", "user_" + self.user.username)
        
        if not os.path.exists(userd_dir):
            os.makedirs(userd_dir)
        super(Image, self).save(*args, **kwargs)
        