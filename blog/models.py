from django.db import models
import os

class Post(models.Model):
    title = models.CharField(max_length=30)                     #CharField() :  문자열 길이 최대 30으로 제한함.
    hook_text = models.CharField(max_length=100, blank=True)    #게시글 요약, 미리보기
    content = models.TextField()                                #TextField() : 문자열 길이 제한 안둠.

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)    #생성 시점에만 시간 저장
    update_at = models.DateTimeField(auto_now=True)         #수정 시점에 시간 업데이트
    #author: 추후 작성 예정                       #author 필드 : 나중에 모델에서 외래키를 구현할때 다룰것.


    def __str__(self):
        return f'[{self.pk}]{self.title}'

    # 상세 페이지로 이동하는 url
    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    # 파일명 추출하여 반환
    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    # 파일 확장자 추출
    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]

# Create your models here.
