from django.urls import reverse
from rest_framework.test import APITestCase


class LogoutTest(APITestCase):
    def setUp(self) -> None:
        self.name = 'name'
        self.password = 'password'
        self.valid_data = {'name': self.name, 'password': self.password}
        self.client.post(reverse('signup'), data=self.valid_data)

    # проверка, что при разлогине возвращается корректный статус
    def test_logout_returns_correct_status_code(self):
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 204)

    # проверка, что при разлогине кука с токеном сбрасывается
    def test_drop_cookie_after_logout(self):
        response = self.client.post(reverse('login'), data=self.valid_data)
        token = response.data.get('token')
        is_token_set = token in str(response.cookies)
        response = self.client.post(reverse('logout'))
        is_token_dropped = token not in str(response.cookies)
        self.assertTrue(is_token_set)
        self.assertTrue(is_token_dropped)
