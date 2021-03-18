"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase
from flask import session

from models import db, connect_db, Message, User
from sqlalchemy.exc import IntegrityError, PendingRollbackError
from sqlalchemy import exc

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
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client, add sample data."""
        db.session.rollback()

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        user = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        user2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        
        db.session.add(user)
        db.session.add(user2)
        db.session.commit()
        self.testuser = User.query.all()[0]
        self.testuser2 = User.query.all()[1]

    def test_signup_view(self):
        """Does the signup page show up"""
        with self.client as c:

            resp = c.get('/signup')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Sign me up!', html)

    def test_signup_success(self):
        """Can the user successfully signup?"""
        with self.client as c:

            resp = c.post('/signup', data={
                    "username": 'testuser3',
                    "password": 'testuser',
                    "email": 'test3@test.com',
                    "image_url": None
                    })
            self.assertEqual(len(User.query.all()), 3)
            self.assertEqual(resp.status_code, 302)
            #ASK ABOUT THIS
            with c.session_transaction() as sess:
                self.assertEqual(sess[CURR_USER_KEY], User.query.all()[2].id)

    def test_signup_duplicate_username(self):
        with self.client as c:
            resp = c.post('/signup', data={
                    "username": 'testuser',
                    "password": 'testuser',
                    "email": 'test4@test.com',
                    "image_url": None
                })

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Username already taken", html)
            db.session.rollback()
            self.assertEqual(len(User.query.all()), 2)
            with c.session_transaction() as sess:
                self.assertEqual(sess.get(CURR_USER_KEY), None)

    #if invalid form fields
        
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


    def test_user_followers(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp=c.get(f'/users/{self.testuser2.id}/followers')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p class="small">Following</p>', html)
    
    def test_user_loggedout_followers(self):
        with self.client as c:
            resp=c.get(f'/users/{self.testuser2.id}/followers', follow_redirects=True)
            
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.",html)

    def test_invalid_user_page(self):
        invalid_user_id = self.testuser2.id + 1
        with self.client as c:
            resp=c.get(f'/users/{invalid_user_id}', follow_redirects=True)

            self.assertEqual(resp.status_code, 404)
    
    def test_user_logout(self)
        with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser.id
        
            resp=c.get("/logout", follow_redirects=True)

            html = resp.get_data(as_text=True)
            
            self.assertIn("Successfully logged out.",html)
            with c.session_transaction() as sess:
                self.assertEqual(sess.get(CURR_USER_KEY), None)
    
    def test_user_valid_login(self):
        with self.client as c:
            resp = c.post("/login", data={
                "username": 'testuser',
                "password": 'testuser',
            }, follow_redirects=True)

            html = resp.get_data(as_text=True)

            with c.session_transaction() as sess:
                self.assertEqual(sess.get(CURR_USER_KEY), self.testuser.id)

            self.assertIn("Hello, testuser!", html)
            self.assertEqual(resp.status_code, 200)
    
    def test_user_invalid_password_login(self):
        with self.client as c:
            resp = c.post("/login", data={
                "username": 'testuser',
                "password": 'testuse',
            })

            html = resp.get_data(as_text=True)
            self.assertIn("Invalid Credentials.", html)
            self.assertEqual(resp.status_code, 200)
            with c.session_transaction() as sess:
                self.assertEqual(sess.get(CURR_USER_KEY), None)
    








    










    
    

