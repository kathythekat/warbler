"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        user = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        user2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.add(user)
        db.session.add(user2)
        db.session.commit()
        self.testuser = User.query.all()[0]
        self.testuser2 = User.query.all()[1]

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
            self.assertEqual(msg.user_id, sess[CURR_USER_KEY])

    def test_delete_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            msg = Message(text="test message", user_id=self.testuser.id)
            db.session.add(msg)
            db.session.commit()
            msg_id = Message.query.one().id
            resp = c.post(f"/messages/{msg_id}/delete")

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(len(Message.query.all()), 0)
    
    def test_add_message_if_loggedout(self):
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)

            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
    
            self.assertIn("Access unauthorized.",html)

    def test_delete_message_if_loggedout(self):
        with self.client as c:
            msg = Message(text="test message", user_id=self.testuser.id)
            db.session.add(msg)
            db.session.commit()
            msg_id = Message.query.one().id
            resp = c.post(f"/messages/{msg_id}/delete", follow_redirects=True)
            
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.",html)
    
    def test_delete_message_if_not_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            msg = Message(text="test message", user_id=self.testuser2.id)
            db.session.add(msg)
            db.session.commit()
            msg_id = Message.query.one().id
            resp = c.post(f"/messages/{msg_id}/delete", follow_redirects=True)
            
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.",html)

    

        
