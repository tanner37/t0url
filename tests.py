import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from flask import Flask

with patch.object(Flask, 'run'):
    import t0url as app_module

app_module.flask_app.config['TESTING'] = True


class T0UrlUpgradeTests(unittest.TestCase):
    def test_python_311_or_newer_runtime(self):
        self.assertGreaterEqual(sys.version_info[:2], (3, 11))

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        app_module.DB = str(Path(self.temp_dir.name) / 'urls')
        self.client = app_module.flask_app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_generated_ids_are_four_uppercase_letters(self):
        for _ in range(20):
            self.assertRegex(app_module.new_id(), r'^[A-Z]{4}$')

    def test_short_url_creation_normalizes_scheme_and_redirects(self):
        response = self.client.post('/', data={'url': 'example.com/path'})
        self.assertEqual(response.status_code, 200)
        short_id = response.get_data(as_text=True).strip().rsplit('/', 1)[1]
        redirect = self.client.get('/' + short_id)
        self.assertEqual(redirect.status_code, 302)
        self.assertEqual(redirect.headers['Location'], 'http://example.com/path')

    def test_invalid_url_is_rejected(self):
        self.assertEqual(self.client.post('/', data={'url': 'not a url'}).status_code, 400)


if __name__ == '__main__':
    unittest.main()
