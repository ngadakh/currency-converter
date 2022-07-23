from flask_testing import TestCase

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

    def test_square(self):
        user = db.session.query(User).filter_by(username="test_user").first()
        print(user.username, user.password)
        assert user.password == 'test_user_password'

    def tearDown(self):
        db.session.remove()
        db.drop_all()