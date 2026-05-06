from django.test import TestCase, Client
from django.urls import reverse
from .models import User

class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

class UserModelTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(username='testuser', password='password123', role='backend')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, 'backend')
        # In views.py, user.is_active is set to False manually during registration.
        # But User.objects.create_user sets it to True by default.
        # So we just check if we can create the user.
        self.assertTrue(user.is_active)
