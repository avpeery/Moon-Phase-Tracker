from server import app
from unittest import TestCase
from flask import session
from model import *
from helpers import *
from testing_seed_data import *


class MoonPhaseTrackerTests(TestCase):
    """Tests Moon Phase Tracker site"""

    def setUp(self):
        """Code to run before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_homepage(self):
        """Tests homepage"""

        result = self.client.get("/")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"<h3>Track the moon", result.data)

    def test_calendar(self):
        """Tests page that displays calendar"""

        result = self.client.get("/calendar")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"<title>Moon Phase Tracker</title>", result.data)


class TestMoonPhaseDatabase(TestCase):
    """Tests moon phase database"""

    def setUp(self):
        """Code to run before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        connect_to_db(app, db_uri="postgresql:///testdb")

        db.create_all()
        test_data()

    def test_homepage(self):
        """Tests homepage"""

        result = self.client.get("/")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"<title>Moon Phase Tracker</title>", result.data)

    def tearDown(self):
        """Code to run after every test"""

        db.session.remove()
        db.drop_all()
        db.engine.dispose()


class TestMoonPhaseLoggedIn(TestCase):
    """Tests site with user logged into session"""

    def setUp(self):
        """Code to run before every test."""

        app.config['TESTING'] = True
        self.client = app.test_client()

        connect_to_db(app, db_uri="postgresql:///testdb")

        db.create_all()
        test_data()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['email'] = 'sample@sample.com'

    def test_login(self):
        """Tests user log in"""

        with self.client as c:
            result = c.post('/login',
                            data={'email': 'sample@sample.com', 'password': 'password'},
                            follow_redirects=True
                            )
            self.assertEqual(result.status_code, 200)
            self.assertIn(b"<title>Moon Phase Tracker</title>", result.data)

    def test_process_registration(self):
        """Tests continuation of registration with email in session"""

        with self.client as c:
            result = c.post('/register', follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"<title>Moon Phase Tracker</title>", result.data)


    def test_settings(self):
        """Tests display setttings"""
        
        with self.client as c:
            result = c.get('/display-settings', follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"<title>Moon Phase Tracker</title>", result.data)


    def test_logout(self):
        """Test logout route"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['email'] = 'sample@sample.com'

            result = self.client.get('/logout', follow_redirects=True)

            self.assertNotIn(b'email', sess)
            self.assertIn(b"<title>Moon Phase Tracker</title>", result.data)

    def tearDown(self):
        """Code to run after every test"""

        db.session.remove()
        db.drop_all()
        db.engine.dispose()




if __name__ == "__main__": 
    import unittest
    unittest.main()