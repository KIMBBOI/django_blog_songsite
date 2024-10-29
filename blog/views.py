from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from .models import Post, Category, Tag, Comment
from .forms import CommentForm
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from django.db.models import Q


# 게시글 목록 보기
class PostList(ListView):
    model = Post  # Post 모델에서 데이터를 가져옴
    ordering = '-pk'  # 최신 글 순서로 정렬
    paginate_by = 4  # 페이지당 4개의 게시글 표시

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        # 카테고리 목록과 분류되지 않은 게시글 수를 추가하여 템플릿에 전달
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context

# 게시글 상세 보기
class PostDetail(DetailView):
    model = Post    # Post 모델에서 데이터 가져옴

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()
        # 카테고리 목록, 분류되지 않은 게시글 수, 댓글 폼 추가
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['comment_form'] = CommentForm
        return context


# 게시글 작성
class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    # 작성 권한 설정 (슈퍼유저나 스태프만 작성 가능)
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    # 폼이 유효할 때 추가 로직 수행
    def form_valid(self, form):
        current_user = self.request.user
        # 작성자 정보를 현재 사용자로 설정
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form)

            # 태그 문자열을 가져와 처리
            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()

                tags_str = tags_str.replace(',', ';')   # 콤마(,)를 세미콜론(;)으로 변환
                tags_list = tags_str.split(';')     # 태그를 세미콜론으로 분리하여 리스트로 저장

                for t in tags_list:
                    # 앞뒤 공백 제거
                    t = t.strip()
                    # 태그를 DB에서 찾거나 생성
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    # 새로운 태그일 경우 슬러그 생성
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)

                return response

            else:
                return redirect('/blog/')


# 게시글 수정하기
class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    template_name = 'blog/post_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        # 기존 태그 정보를 '; '로 구분하여 전달
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)

        return context

    # 수정 폼이 유효할 때 처리
    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        # 기존 태그 제거
        self.object.tags.clear()

        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug =slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)

        return response


    # 게시글 작성자만 수정할 수 있게. - dispatch()로 요청 방식 판단 (GET 방식인 지, POST 방식인 지)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied



# 댓글 수정
class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    # 댓글 폼 사용
    form_class = CommentForm

    # 댓글 작성자만 수정할 수 있도록 권한 검사
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

# 검색 기능
class PostSearch(PostList):

    paginate_by = None

    def get_queryset(self):
        # 검색어 가져오기
        q = self.kwargs['q']
        # 검색어가 제목, 내용, 태그에 포함된 게시글 목록 필터링
        post_list = Post.objects.filter(
            Q(title__contains=q) | Q(content__contains=q) | Q(tags__name__contains=q)
        ).distinct()
        return post_list

    def get_context_data(self, **kwargs):
        context = super(PostSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'Search: {q} ({self.get_queryset().count()})'

        return context


# 카테고리별 게시글 필터링
def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)   # 카테고리가 없는 게시글 필터링
    else:
        category = Category.objects.get(slug=slug)  # 슬러그로 카테고리 찾기
        post_list = Post.objects.filter(category=category)  # 해당 카테고리의 게시글 필터링

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category': category,
        }
    )

# 태그별 게시글 필터링
def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'tag': tag,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
        }
    )


# 댓글 등록
def new_comment(request, pk):
    if request.user.is_authenticated:
        # 게시글 가져오기
        post = get_object_or_404(Post, pk=pk)

        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                # 댓글과 게시글 연결
                comment.post = post
                comment.author = request.user
                comment.save()
                # 댓글 저장 후 해당 위치로 이동
                return redirect(comment.get_absolute_url())
            else:
                return redirect(post.get_absolute_url())
        # POST 요청이 아닌 경우 권한 거부
        else:
            raise PermissionDenied

# 댓글 삭제
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied












