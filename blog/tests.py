from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Category, Post


class CategoryModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Category.objects.create(name='TestCategory', slug='test-category')

    def test_name_label(self):
        category = Category.objects.get(id=1)
        field_label = category._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'name')

    def test_slug_label(self):
        category = Category.objects.get(id=1)
        field_label = category._meta.get_field('slug').verbose_name
        self.assertEquals(field_label, 'slug')

    def test_created_label(self):
        category = Category.objects.get(id=1)
        field_label = category._meta.get_field('created').verbose_name
        self.assertEquals(field_label, 'created')

    def test_updated_label(self):
        category = Category.objects.get(id=1)
        field_label = category._meta.get_field('updated').verbose_name
        self.assertEquals(field_label, 'updated')

    def test_name_max_length(self):
        category = Category.objects.get(id=1)
        max_length = category._meta.get_field('name').max_length
        self.assertEquals(max_length, 20)

    def test_slug_max_length(self):
        category = Category.objects.get(id=1)
        max_length = category._meta.get_field('slug').max_length
        self.assertEquals(max_length, 20)

    def test_object_name_is_name(self):
        category = Category.objects.get(id=1)
        expected_object_name = category.name
        self.assertEquals(expected_object_name, str(category))

    def test_get_absolute_url(self):
        category = Category.objects.get(id=1)
        url = reverse('category', args=[str(category.slug)])
        self.assertEquals(url, category.get_absolute_url())


# class PostModelTest(TestCase):

#     def test_get_previous_post(self):
#         post = Post.objects.get(id=1)
#         previous_post = Post.objects.create(
#             title='Previous post', slug='previous-post',
#             author=post.author, category=post.category,
#             excerpt='This is the previous post', body='Previous post body')
#         previous_post.publish = post.publish - timezone.timedelta(days=1)
#         previous_post.save()

#         self.assertEqual(post.get_previous_post(), previous_post)

#     def test_get_next_post(self):
#         post = Post.objects.get(id=1)
#         next_post = Post.objects.create(
#             title='Next post', slug='next-post',
#             author=post.author, category=post.category,
#             excerpt='This is the next post', body='Next post body')
#         next_post.publish = post.publish + timezone.timedelta(days=1)
#         next_post.save()

#         self.assertEqual(post.get_next_post(), next_post)


class PostModelTest(TestCase):

    # @classmethod
    def setUp(self):
        # Set up non-modified objects used by all test methods
        self.user = User.objects.create(username='testuser')
        self.category = Category.objects.create(name='testcategory')
        self.post1 = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            category=self.category,
            excerpt='This is a test post.',
            body='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            image='test.jpg',
            image_caption='Test Image Caption',
            publish='2023-03-11 12:00:00',
            updated='2023-03-11 13:00:00',
            status=Post.Status.PUBLISHED,
            page_views=100,
            read_time=10,
            sponsored=True,
            enable_comments=True,
        )
        self.post1.created = timezone.now() - timezone.timedelta(days=8)
        self.post1.save()

        self.post2 = Post.objects.create(
            title='Test Post2',
            slug='test-post2',
            author=self.user,
            category=self.category,
            excerpt='This is a test post2.',
            body='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            image='test.jpg',
            image_caption='Test Image Caption',
            publish='2023-03-11 11:00:00',
            created='2023-03-10 11:00:00',
            updated='2023-03-11 12:00:00',
            status=Post.Status.DRAFT,
            page_views=100,
            read_time=10,
            sponsored=False,
            enable_comments=True,
        )

    def test_title_max_length(self):
        # post = Post.objects.get(id=1)
        max_length = self.post1._meta.get_field('title').max_length
        self.assertEquals(max_length, 250)

    def test_slug_unique_for_date(self):
        # post = Post.objects.get(id=1)
        unique_for_date = self.post1._meta.get_field('slug').unique_for_date
        self.assertEquals(unique_for_date, 'publish')

    def test_category_related_name(self):
        # category = Category.objects.get(id=1)
        related_name = self.category._meta.get_field('posts').related_name
        self.assertEquals(related_name, 'posts')

    def test_author_related_name(self):
        # user = User.objects.get(id=1)
        related_name = self.user._meta.get_field('posts').related_name
        self.assertEquals(related_name, 'posts')

    def test_status_choices(self):
        # post = Post.objects.get(id=1)
        choices = self.post1._meta.get_field('status').choices
        self.assertEquals(choices, [('DF', 'Draft'), ('PB', 'Published')])

    def test_get_absolute_url(self):
        # post = self.post1
        post = Post.objects.get(id=1)
        expected_url = reverse('post', args=[post.publish.year,
                                             post.publish.month,
                                             post.publish.day,
                                             post.slug])
        self.assertEqual(post.get_absolute_url(), expected_url)

    def test_word_count(self):
        post = self.post1
        # post = Post.objects.get(id=1)
        # Create a post with 8 words
        post.body = 'This is a test post with 8 words.'
        post.save()

        self.assertEqual(post.word_count, 8)

    def test_save_method(self):
        from unittest.mock import patch
        # category = Category.objects.get(id=1)
        category = self.category
        # post = Post.objects.get(id=1)
        # post2 = Post.objects.get(id=2)
        post = self.post1
        post2 = self.post2

        # Check that the sponsored flag is being set correctly
        self.assertTrue(post.sponsored)

        # Check that the other sponsored post has been updated to False
        sponsored_posts = Post.objects.filter(sponsored=True)
        self.assertEqual(len(sponsored_posts), 1)
        self.assertEqual(sponsored_posts[0].pk, post.pk)

        # Check that ping_google is called after saving a post
        with patch('blog.models.ping_google') as mock_ping_google:
            post.save()
            mock_ping_google.assert_called_once()

    def test_published_manager(self):
        user = self.user
        category = self.category
        published_post = self.post1
        # user = User.objects.get(id=1)
        # category = Category.objects.get(id=1)
        # published_post = Post.objects.get(id=1)
        # Create a draft post
        draft_post = Post.objects.create(
            title='Draft Post',
            slug='draft-post',
            author=user,
            category=category,
            excerpt='This is a draft post',
            body='This is the body of a draft post'
        )

        # Use the published manager to get published posts
        published_posts = Post.published.all()

        # Assert that only the published post is returned
        self.assertEqual(list(published_posts), [published_post])

    def test__str__(self):
        # post = Post.objects.get(id=1)
        post = self.post1
        post_title = str(post)
        self.assertEqual(post_title, 'Test Post')



from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone

from blog.models import Post, Category
from blog.views import home


class HomeViewTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Create some test data for the database
        cls.user = User.objects.create(username='testuser')
        cls.category = Category.objects.create(name='Test Category', slug='test-category')
        cls.post1 = Post.objects.create(
            title='Test Post1',
            slug='test-post1',
            author=cls.user,
            category=cls.category,
            excerpt='This is a test post1.',
            body='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            image='test.jpg',
            image_caption='Test Image Caption',
            publish='2023-03-11 11:00:00',
            created='2023-03-10 11:00:00',
            updated='2023-03-11 12:00:00',
            status=Post.Status.PUBLISHED,
            page_views=100,
            read_time=10,
            sponsored=True,
            enable_comments=True,
        )
        # cls.post1.category.add(cls.category)
        # cls.post1.save()
        cls.post2 = Post.objects.create(
            title='Test Post2',
            slug='test-post2',
            author=cls.user,
            category=cls.category,
            excerpt='This is a test post2.',
            body='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            image='test.jpg',
            image_caption='Test Image Caption',
            publish='2023-03-11 11:00:00',
            created='2023-03-10 11:00:00',
            updated='2023-03-11 12:00:00',
            status=Post.Status.PUBLISHED,
            page_views=100,
            read_time=10,
            sponsored=False,
            enable_comments=True,
        )
        # cls.post2.category.add(cls.category)
        # cls.post2.save()
        
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        
    def test_home_view(self):
        # Create a request object
        request = self.factory.get(reverse('home'))
        
        # Get the response from the view
        response = home(request)
        
        # Check that the response has the expected status code
        self.assertEqual(response.status_code, 200)
        
        # Check that the response contains the latest posts and the sponsored post
        self.assertContains(response, self.post1.title)
        self.assertContains(response, self.post2.title)
        self.assertContains(response, 'Sponsored')
        
        # Check that the response contains the post categories
        self.assertContains(response, self.category.name)
        
        # Check that the response contains the trending posts
        self.assertContains(response, 'Trending')
        
        # Check that the response contains the most viewed posts
        self.assertContains(response, self.post1.title)
        self.assertContains(response, self.post2.title)
