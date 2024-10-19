from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown
import os


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)    #고유 url 만들때

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'

    class Meta:
        verbose_name_plural = 'Categories'      #admin 페이지에서 category 이름 지정


class Post(models.Model):
    title = models.CharField(max_length=30)                     #CharField() :  문자열 길이 최대 30으로 제한함.
    hook_text = models.CharField(max_length=100, blank=True)    #게시글 요약, 미리보기
    content = MarkdownxField()                                #TextField() : 문자열 길이 제한 안둠.

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)    #생성 시점에만 시간 저장
    update_at = models.DateTimeField(auto_now=True)         #수정 시점에 시간 업데이트


    #author: 추후 작성 예정                       #author 필드 : 나중에 모델에서 외래키를 구현할때 다룰것.
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)  #on_delete=models.CASCADE : '이 포스트의 작성자가 데이터베이스에서 삭제되었을 때 이 포스트도 같이 삭제한다.'
    #author = models.ForeignKey(User, on_delete=models.CASCADE)  #on_delete=models.CASCADE : '이 포스트의 작성자가 데이터베이스에서 삭제되었을 때 이 포스트도 같이 삭제한다.'

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f'[{self.pk}]{self.title} :: {self.author}'

    # 상세 페이지로 이동하는 url
    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    # 파일명 추출하여 반환
    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    # 파일 확장자 추출
    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]

    def get_content_markdown(self):
        return markdown(self.content)

# Create your models here.
