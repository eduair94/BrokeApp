import unittest
from main import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
    
    def test_health_endpoint(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'OK')

    def test_hello_endpoint(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Hello! This is a sample CI/CD application')

if __name__ == '__main__':
    unittest.main()
