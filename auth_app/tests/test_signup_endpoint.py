from django.urls import reverse
from rest_framework.test import APITestCase

from auth_app.models import User


class SignupTest(APITestCase):
    def setUp(self) -> None:
        self.name = 'name'
        self.password = 'password'
        self.valid_data = {'name': self.name, 'password': self.password}

    # проверяем что при корректном вводе данных возвращается статус о создании объекта
    def test_get_correct_status_code(self):
        response = self.client.post(reverse('signup'), data=self.valid_data)
        self.assertEqual(response.status_code, 201)

    # проверяем что при отсутствии записи в поле пароль возвращается статус плохой запрос
    def test_get_invalid_status_code(self):
        response = self.client.post(reverse('signup'), data={'data': 'data'})
        self.assertEqual(response.status_code, 400)

    # проверяем успешное создание записи в базе данных
    def test_user_is_created(self):
        self.client.post(reverse('signup'), data=self.valid_data)
        user = User.objects.filter(name=self.name).first()
        self.assertEqual(user.name, self.name)

    # проверяем что нельзя создать двух пользователей с одним именем
    def test_cannot_create_user_with_same_name_twice(self):
        self.client.post(reverse('signup'), data=self.valid_data)
        response = self.client.post(reverse('signup'), data=self.valid_data)
        users_length = User.objects.filter(name=self.name).count()
        self.assertEqual(users_length, 1)
        self.assertEqual(response.status_code, 400)
