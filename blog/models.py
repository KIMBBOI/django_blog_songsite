from django.db import models
import os

class Post(models.Model):
    title = models.CharField(max_length=30)     #CharField() :  문자열 길이 최대 30으로 제한함.
    hook_text = models.CharField(max_length=100, blank=True)
    content = models.TextField()                #TextField() : 문자열 길이 제한 안둠.

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d', blank=True)

    created_at = models.DateTimeField(auto_now=True)
    update_at = models.DateTimeField(auto_now=True)
    #author: 추후 작성 예정                       #author 필드 : 나중에 모델에서 외래키를 구현할때 다룰것.


    def __str__(self):
        return f'[{self.pk}]{self.title}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]

# Create your models here.
