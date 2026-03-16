from django.db import models
from api.User.model import CustomUser
from django.utils.deconstruct import deconstructible
import uuid
import os

# @deconstructible
# class UploadToUserFolder:
#     def __init__(self, base_path):
#         self.base_path = base_path

#     def __call__(self, instance, filename):
#         ext = filename.split('.')[-1]
#         new_name = f"{uuid.uuid4()}.{ext}"
#         return os.path.join(self.base_path, new_name)

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    contact_no = models.CharField(max_length=15, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    # logo = models.ImageField(upload_to=UploadToUserFolder('clientData/%Y/%m/%d/'), null=True, blank=True)
    # digital_signature = models.ImageField(upload_to=UploadToUserFolder('clientData/%Y/%m/%d/'), null=True, blank=True)


    def __str__(self):
        return self.user.username  
    

#---Remember----#
# if add more fields in this model then update its own serializer as well as user's serializer
    