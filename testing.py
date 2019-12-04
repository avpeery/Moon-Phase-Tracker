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
        self.assertIn(b"<h1>Moon Phase Tracker</h1>", result.data)


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
        self.assertIn(b"<h1>Moon Phase Tracker</h1>", result.data)

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
            self.assertIn(b"<h1>Moon Phase Tracker</h1>", result.data)

    def test_logout(self):
        """Test logout route"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['email'] = 'sample@sample.com'

            result = self.client.get('/logout', follow_redirects=True)

            self.assertNotIn(b'email', session)
            self.assertIn(b'<h1>Moon Phase Tracker</h1>', result.data)

    def tearDown(self):
        """Code to run after every test"""

        db.session.remove()
        db.drop_all()
        db.engine.dispose()




if __name__ == "__main__": 
    import unittest
    unittest.main()