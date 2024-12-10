import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import unittest
import warnings
from api import app


class APITests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.app = app.test_client()

        warnings.simplefilter("ignore", category=DeprecationWarning)

    def test_index_page(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "<p>Hello World!</p>")

    def test_get_dogs(self):
        response = self.app.get("/dogs")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Chambe" in response.data.decode())


if __name__ == "__main__":
    unittest.main()
