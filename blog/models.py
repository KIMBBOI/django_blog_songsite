from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown
import os


# Tag 모델: 게시글에 부여할 태그를 위한 모델
class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'


# Category 모델: 게시글의 카테고리를 위한 모델
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)    #고유 url 만들때

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'

    class Meta:# Admin 페이지에서 표시할 때 'Categories'로 표시하도록 설정
        verbose_name_plural = 'Categories'


# Post 모델: 블로그 게시글을 위한 모델
class Post(models.Model):
    title = models.CharField(max_length=30)                     #CharField() :  문자열 길이 최대 30으로 제한함.
    hook_text = models.CharField(max_length=100, blank=True)    #게시글 요약, 미리보기
    content = MarkdownxField()                                #TextField() : 문자열 길이 제한 안둠.

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d', blank=True)

    # 게시글 생성 시간 (자동 생성)
    created_at = models.DateTimeField(auto_now_add=True)    #생성 시점에만 시간 저장
    # 게시글 수정 시간 (자동 업데이트)
    update_at = models.DateTimeField(auto_now=True)         #수정 시점에 시간 업데이트


    # 작성자 필드: User 모델과 외래키 관계 (작성자가 삭제될 경우, 게시글은 NULL로 설정)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    # 카테고리 필드: Category 모델과 외래키 관계, NULL 허용, 비워둘 수 있음
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    # 태그 필드: Tag 모델과 다대다 관계, 태그는 여러 개 설정 가능
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

    def get_avatar_url(self):
        # 작성자가 소셜 계정을 가지고 있는 경우, 아바타 URL 반환
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        # 그렇지 않은 경우 기본 아바타 URL 반환
        else:
            return f'https://doitdjango.com/avatar/id/2509/c94d6520730cd566/svg/{self.author.email}'


# Comment 모델: 게시글에 달린 댓글을 위한 모델
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.author}::{self.content}'

    def get_absolute_url(self):
        return f'{self.post.get_absolute_url()}#comment-{self.pk}'

    # 구글 아바타 설정
    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return 'https://doitdjango.com/avatar/id/2509/c94d6520730cd566/svg/{self.author.email}'
