import unittest
from app import app, db
from models import User, Post, Tag

class BloglyTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_creation(self):
        """Test that a user can be created and properly saved to the test db"""
        response = self.client.post('/users/new', data={
            'first_name': 'Test',
            'last_name': 'User',
            'image_url': 'https://example.com/test.png'
        })
        self.assertEqual(response.status_code, 302)
        with app.app_context():
            user = User.query.filter_by(first_name='Test').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.last_name, 'User')

    def test_users_list(self):
        """Test the user list page"""
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)

    def test_user_detail(self):
        """Test user detail page"""
        with app.app_context():
            user = User(first_name="Jane", last_name="Doe", image_url="https://example.com/jane.png")
            db.session.add(user)
            db.session.commit()
            response = self.client.get(f'/users/{user.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Jane Doe', response.data)
        self.assertIn(b'https://example.com/jane.png', response.data)

    def test_user_edit(self):
        """Test editing a user's info"""
        with app.app_context():
            user = User(first_name="Billy", last_name="Smith", image_url="https://example.com/billy.png")
            db.session.add(user)
            db.session.commit()

            response = self.client.post(f'/users/{user.id}/edit', data={
                'first_name': 'William',
                'last_name': 'Smith',
                'image_url': 'https://example.com/william.png'
            })

            self.assertEqual(response.status_code, 302)

            updated_user = User.query.get(user.id)


            # Check that the user details are updated
            self.assertEqual(updated_user.first_name, 'William')
            self.assertEqual(updated_user.image_url, 'https://example.com/william.png')

    def test_user_deletion(self):
        """Test deleting a user"""
        with app.app_context():
            user = User(first_name="Charlie", last_name="Brown", image_url="https://example.com/charlie.png")
            db.session.add(user)
            db.session.commit()

            response = self.client.post(f'/users/{user.id}/delete')
            self.assertEqual(response.status_code, 302)

            deleted_user = User.query.get(user.id)
            self.assertIsNone(deleted_user)

    def test_default_image(self):
        """Test that user creation defaults to the default image if none is provided"""
        response = self.client.post('/users/new', data={
            'first_name': 'No',
            'last_name': 'Image',
            'image_url': ''
        })
        self.assertEqual(response.status_code, 302)
        with app.app_context():
            user = User.query.filter_by(first_name='No').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.image_url, "https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png")

    ##################

    def test_post_creation(self):
        """Test that a user can create a post"""
        with app.app_context():
            user = User(first_name="Test", last_name="User", image_url="https://example.com/test.png")
            db.session.add(user)
            db.session.commit()

            response = self.client.post(f'/users/{user.id}/posts/new', data={
                'title': 'Test Post',
                'content': 'This is a test post.'
            })

            self.assertEqual(response.status_code, 302)
            post = Post.query.filter_by(title='Test Post').first()
            self.assertIsNotNone(post)
            self.assertEqual(post.content, 'This is a test post.')

            # fetch the updated user page to check if the post appears
            response = self.client.get(f'/users/{user.id}')
            self.assertIn(b'Test Post', response.data)

    def test_post_edit(self):
        """Test editing a users post details"""
        with app.app_context():
            user = User(first_name="Test", last_name="User", image_url="https://example.com/test.png")
            db.session.add(user)
            db.session.commit()

            post = Post(title="Old Title", content="Old content.", user_id=user.id)
            db.session.add(post)
            db.session.commit()

            response = self.client.post(f'/posts/{post.id}/edit', data={
                'title': 'New Title',
                'content': 'New content.'
            })

            self.assertEqual(response.status_code, 302)

            updated_post = Post.query.get(post.id)
            self.assertEqual(updated_post.title, 'New Title')
            self.assertEqual(updated_post.content, 'New content.')

    def test_post_deletion(self):
        """Test deleting a users post"""
        with app.app_context():
            user = User(first_name='Test', last_name='User', image_url='https://example.com/test.png')
            db.session.add(user)
            db.session.commit()

            post = Post(title='Title to Delete', content='Content to delete.', user_id=user.id)
            db.session.add(post)
            db.session.commit()

            response = self.client.post(f'/posts/{post.id}/delete')
            self.assertEqual(response.status_code, 302)

            deleted_post = Post.query.get(post.id)
            self.assertIsNone(deleted_post)

    def test_tag_creation(self):
        """Test creating a Tag."""
        with app.app_context():
            response = self.client.post('/tags/new', data={"name": "Test Tag"}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test Tag', response.data)

    def test_tag_list(self):
        """Test listing all Tags."""
        with app.app_context():
            tag = Tag(name="Test Tag")
            db.session.add(tag)
            db.session.commit()

            response = self.client.get('/tags')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test Tag', response.data)

    def test_tag_detail(self):
        """Test viewing a single Tag."""
        with app.app_context():
            tag = Tag(name="Test Tag")
            db.session.add(tag)
            db.session.commit()

            response = self.client.get(f'/tags/{tag.id}')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test Tag', response.data)

    def test_tag_edit(self):
        """Test editing a Tag."""
        with app.app_context():
            tag = Tag(name="Test Tag")
            db.session.add(tag)
            db.session.commit()

            edit_data = {
                "name": "Updated Tag"
            }

            response = self.client.post(f'/tags/{tag.id}/edit', data=edit_data, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Updated Tag', response.data)

    def test_tag_delete(self):
        """Test deleting a Tag."""
        with app.app_context():
            tag = Tag(name="Test Tag")
            db.session.add(tag)
            db.session.commit()

            response = self.client.post(f'/tags/{tag.id}/delete', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn(b'Test Tag', response.data)