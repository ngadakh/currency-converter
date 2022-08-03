from operator import rshift
from click import confirm
from flask_testing import TestCase
from flask import url_for

from app.app import app, db
from app.model import User


class BaseTestCase(TestCase):
    """A base test case class"""

    def create_app(self):
        app.config.from_object('config.TestConfiguration')
        return app

    def setUp(self):
        db.create_all()
        user = User("test_user", "test_user_password", "test_user@gmail.com", "test_user.png", "USD")
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class UserTestCase(BaseTestCase):
    """Test cases of user's action like login and logout"""

    def login_user(self):
        response = self.client.post(
            url_for('login'), 
            data={'username': 'test_user', 'password': 'test_user_password'}
        )
        return response

    def test_login_logout(self):
        response = self.login_user()
        self.assert_200(response)

        response = self.client.get(url_for('logout'))
        assert 302 == response.status_code
     

    def test_user_profile(self):
        response = self.login_user()
        response = self.client.get(url_for('profile'))
        self.assert200(response)
    
    def test_user_signup(self):
        response = self.client.post(
            url_for('signup'),
            content_type='multipart/form-data',  
            data=dict(
                username='new_test_user',
                email='new_test_user@test.com',
                password='test_user_password',
                confirm='test_user_password',
                # profile_photo='new_test_user_photo.png',
                default_currency='USD'
            ),
            follow_redirects=True
        )
        print(dir(response), response.data)
        self.assert200(response)
        