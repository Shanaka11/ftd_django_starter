from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth.models import User

# Create your tests here.
class RegistrationTestCase(APITestCase):

    def test_registration(self):
        data = {
            "email": "shanakaabeysingheadd@gmail.com",
            "password": "12345",
            "firstName": "Shanaka",
            "lastName": ""
        }

        response = self.client.post("/api/user/create_user/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LoginTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="shanakaabeysinghe@gmail.com", password="12345")

    def test_login(self):
        data = {
            "username": "shanakaabeysinghe@gmail.com",
	        "password": "12345"
        }

        response = self.client.post("/api/user/token/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_login_fail(self):
        data = {
            "username": "shanakaabeysinghe@gmail1.com",
	        "password": "12345"
        }
        response = self.client.post("/api/user/token/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# Rest of the user actions Get / Update / Remove
class UserCrudTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="shanakaabeysinghe@gmail.com", first_name="Shanaka", password="12345")
        self.user = User.objects.create_user(username="shanakaabeysinghe1@gmail.com", first_name="Bandara", password="12345", is_staff=True)
        self.api_authenticate()

    def api_authenticate(self):
        data = {
            "username": "shanakaabeysinghe1@gmail.com",
	        "password": "12345"
        }
        response = self.client.post("/api/user/token/", data)

        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_list(self):
        response = self.client.get("/api/user/")
        self.assertEqual(len(response.data), 2)

    def test_detail(self):
        response = self.client.get("/api/user/1")
        self.assertEqual(response.data['first_name'], 'Shanaka')

    def test_update(self):
        data = {
            "firstName": "shanaka1",
	        "lastName": "bandara1"
        }
        response = self.client.put("/api/user/update/1", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(id=1)
        self.assertEqual(user.first_name, 'shanaka1')
        self.assertEqual(user.last_name, 'bandara1')

    def test_delete(self):
        response = self.client.delete("/api/user/remove/1")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(id=1)
        self.assertEqual(user.is_active, False)