import unittest
from app import app, db
from models import User

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


