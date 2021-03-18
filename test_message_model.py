from unittest import TestCase

from app import app
from models import db, connect_db, Message, User, Like
import datetime
from flask_bcrypt import Bcrypt

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///warbler_test'
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True

bcrypt = Bcrypt()
db.drop_all()
db.create_all()

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.session.rollback()

        User.query.delete()
        Message.query.delete()
        Like.query.delete()

        u1 = User(
            email="test@test.com",
            username="testuser1",
            password=bcrypt.generate_password_hash('HASHED PASSWORD').decode('UTF-8')
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password=bcrypt.generate_password_hash('HASHED PASSWORD').decode('UTF-8')
        )
        
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.u1 = User.query.all()[0]
        self.u2 = User.query.all()[1]

        m1 = Message(
            text="test message",
            user_id=self.u1.id
        )

        db.session.add(m1)
        db.session.commit()
        self.m1 = Message.query.all()[0]
        self.now = datetime.datetime.utcnow()
        self.client = app.test_client()

    def test_message_model(self):
        """Does basic model work?"""

        self.assertEqual(self.m1.text, "test message")
        self.assertAlmostEqual(self.m1.timestamp, self.now, delta=datetime.timedelta(minutes=1))
        # Message should have 1 user and 0 likers
        self.assertIsInstance(self.m1.user, User)
        self.assertEqual(self.m1.user.id, self.u1.id)
        self.assertEqual(len(self.m1.likers), 0)

    def test__repr__(self):
        """Does the repr method work as expected?"""

        response = self.m1.__repr__()

        self.assertEqual(response, f"<Message #{self.m1.id}: {self.m1.text}, {self.m1.user_id}>")

    def test_user_messages(self):
        """Does user have new messasge in messages list? """
        new_message = Message(text="test message 2", user_id=self.u1.id)
        db.session.add(new_message)
        db.session.commit()
        self.assertEqual(len(self.u1.messages), 2)

    def test_liking_message(self):
        """ Does user like a message? """
        like = Like(user_id=self.u2.id, message_id=self.m1.id)
        db.session.add(like)
        db.session.commit()
        self.assertEqual(len(self.m1.likers), 1)
        self.assertEqual(len(self.u2.liked_messages), 1)
