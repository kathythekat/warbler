"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# USER_DATA = {
#     "username": "testuser",
#     "password": "password",
#     "email": "user@gmail.com",
# }

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User(
            email="test@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test@gmail.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        self.client = app.test_client()
        self.u1 = User.query.all()[0]
        self.u2 = User.query.all()[1]
    

    def test_user_model(self):
        """Does basic model work?"""

        # User should have no messages & no followers
        self.assertEqual(len(self.u1.messages), 0)
        self.assertEqual(len(self.u1.followers), 0)

    def test__repr__(self):
        """Does the repr method work as expected?"""

        response = self.u1.__repr__()

        self.assertEqual(response, f"<User #{self.u1.id}: {self.u1.username}, {self.u1.email}>")
    

    def test_is_following(self):
        """Is this user following other user?"""
      
        follow = Follows(user_being_followed_id=self.u2.id, user_following_id=self.u1.id)
        db.session.add(follow)
        db.session.commit()

        self.assertEqual(self.u1.is_following(self.u2), True)
        self.assertEqual(self.u2.is_following(self.u1), False)
    
    
    def test_is_followed_by(self):
        """Is this user followed by other user?"""
        follow = Follows(user_being_followed_id=self.u2.id, user_following_id=self.u1.id)
        db.session.add(follow)
        db.session.commit()

        self.assertEqual(self.u2.is_followed_by(self.u1), True)
        self.assertEqual(self.u1.is_followed_by(self.u2), False)


