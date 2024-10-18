from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag


class TestView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_katie = User.objects.create_user(username='katie', password='samepassword')
        self.user_cold = User.objects.create_user(username='cold', password='samepassword')

        self.user_katie.is_staff = True
        self.user_katie.save()

        # 테스트 코드 - 카테고리 이름 추가 (programming, etc)
        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_etc = Category.objects.create(name='etc', slug='etc')

        # 3개의 테스트 태그 추가
        self.tag_python_kor = Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')
        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_hello = Tag.objects.create(name='hello', slug='hello')

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello World. We are the World.',
            category=self.category_programming,
            author=self.user_katie
        )
        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content='1등이 전부는 아니잖아요?',
            category=self.category_etc,
            author=self.user_cold
        )

        self.post_003 = Post.objects.create(
            title='세 번째 포스트입니다.',
            content='Category가 없을 수도 있지',
            author=self.user_cold
        )
        self.post_003.tags.add(self.tag_python_kor)
        self.post_003.tags.add(self.tag_python)


    # 1.4 내비게이션 바가 있다.
    # 1.5. Blog , About Me 라는 문구가 내비게이션 바에 있다，
    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text='Do It Django')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')


    def test_post_list(self):

        # 포스트가 있는 경우
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        # 3개의 포스트 카드에 원하는 내용이 있는지 확인
        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn(self.post_003.author.username.upper(), post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)

        self.assertIn(self.user_katie.username.upper(), main_area.text)
        self.assertIn(self.user_cold.username.upper(), main_area.text)

        # 포스트가 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')

        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)



    def test_post_detail(self):

        # 1. 2. 그 포스트의 url은 '/blog/1/' 이다.
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        # 2. 첫 번째 포스트의 상세 페이지 테스트
        # 2. 1. 첫 번째 포스트의 url로 접근하면 정상적으로 작동한다(status code: 200).
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 2.2. 포스트 목록 페이지와 똑같은 내비게이션 바가 있다.
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 2.3. 첫 번째 포스트의 제목이 웹 브라우저 탬 타이 에 들어 있다.
        self.assertIn(self.post_001.title, soup.title.text)

        # 2.4. 첫 번째 포스트의 제목이 포스트 영역에 있다.
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)

        # 2.5. 첫 번째 포스트의 작성자(author) 가 포스트 영역에 있다(아직 구현할 수 없음)
        self.assertIn(self.user_katie.username.upper(), post_area.text)

        # 2.6. 첫 번째 포스트의 (c ontent)OI 포스트 영역에 있다.
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)


    # 카테고리 페이지 테스트
    def test_category_page(self):

        # 카테고리 페이지 url 오픈 확인.
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        # 네비게이션바 & 카테고리 카드 구성 확인.
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 페이지 상단에 카테고리 뱃지 노출 확인.
        # <h1>태그에 카테고리 이름 유무 확인.
        self.assertIn(self.category_programming.name, soup.h1.text)

        # 카테고리 'programming' 유무 확인.
        # 해당하는 포스트 노출 확인.
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    # 카테고리 카드 테스트
    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')

        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_etc.name} ({self.category_etc.post_set.count()})', categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)


    # 태그 페이지 테스트
    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_hello.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)


    # (폼태그) 포스트 작성 페이지 테스트
    def test_create_post(self):

        # 로그인 하지 않으면 status code가 200이면 안됨.
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff가 아닌 cold가 로그인을 한다.
        self.client.login(username='cold', password='samepassword')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # 로그인 시도
        self.client.login(username='katie', password='samepassword')

        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('새 게시글 작성', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post(
            '/blog/create_post/',
            {
                'title': 'Post Form 만들기',
                'content': "Post Form 페이지를 만듭시다.",
                'tags_str': 'new tag; 한글 태그, python'
            }
        )
        self.assertEqual(Post.objects.count(), 4)
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post Form 만들기")
        self.assertEqual(last_post.author.username, 'katie')

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertTrue(Tag.objects.count(), 5)


    # 게시글 수정하기 테스트
    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        # 로그인하지 않은 경우
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        # 로그인은 했지만 작성자가 아닌 경우
        self.assertNotEqual(self.post_003.author, self.user_katie)
        self.client.login(
            username = self.user_katie.username,
            password = 'samepassword'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        # 작성자(kaite)가 접근하는 경우
        self.client.login(
            username = self.post_003.author.username,
            password = 'samepassword'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('게시글 수정', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('파이썬 공부; python', tag_str_input.attrs['value'])

        response = self.client.post(
            update_post_url,
            {
                'title': '세 번째 포스트를 수정했습니다.',
                'content': 'hello world !!!!!!!!!!!!!',
                'category': self.category_etc.pk,
                'tags_str': '파이썬 공부; 한글 태그, some tag, python'
            },
            follow = True
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세 번째 포스트를 수정했습니다.', main_area.text)
        self.assertIn('hello world !!!!!!!!!!!!!', main_area.text)
        self.assertIn(self.category_etc.name, main_area.text)
        self.assertIn('파이썬 공부', main_area.text)
        self.assertIn('한글 태그', main_area.text)
        self.assertIn('some tag', main_area.text)
        self.assertIn('python', main_area.text)
















