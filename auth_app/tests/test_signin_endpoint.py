import os

import jwt
from django.urls import reverse
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APITestCase

SECRET_KEY = os.environ.get('SECRET_KEY')


class SignInTest(APITestCase):
    def setUp(self) -> None:
        self.name = 'name'
        self.password = 'password'
        self.valid_data = {'name': self.name, 'password': self.password}
        self.client.post(reverse('signup'), data=self.valid_data)

    # проверка логина с валидными данными
    def test_response_200_with_valid_data(self):
        response = self.client.post(reverse('login'), data=self.valid_data)
        self.assertEqual(response.status_code, 200)

    # проверка попытки логина без ввода пароля
    def test_response_403_with_only_name_data(self):
        response = self.client.post(reverse('login'), data={'name': self.name})
        self.assertEqual(response.status_code, 403)

    # проверка найти юзера по несуществующему имени
    def test_user_not_found_by_name(self):
        response = self.client.post(reverse('login'), data={'name': 'noname', 'password': self.password})
        is_error_message = 'Не найден пользователь с таким именем' in str(response.data.get('detail'))
        self.assertRaises(AuthenticationFailed)
        self.assertTrue(is_error_message)

    # проверка попытки войти под неправильным паролем
    def test_login_with_invalid_password(self):
        response = self.client.post(reverse('login'), data={'name': self.name, 'password': 'invalid'})
        is_error_message = 'Неправильный пароль' in str(response.data.get('detail'))
        self.assertRaises(AuthenticationFailed)
        self.assertTrue(is_error_message)

    # проверяем что при корректном логине возвращается jwt токен авторизации
    def test_get_authentication_token(self):
        response = self.client.post(reverse('login'), data=self.valid_data)
        token = response.data.get('token')
        username = None
        if token:
            username = jwt.decode(token, SECRET_KEY, algorithms=['HS256']).get('name')
        self.assertEqual(username, self.name)

    # проверяем что после логина устанавливается кука с токеном авторизации
    def test_check_if_token_in_a_cookie(self):
        response = self.client.post(reverse('login'), data=self.valid_data)
        token = response.data.get('token')
        is_cookie_set = token in str(response.cookies)
        self.assertTrue(is_cookie_set)
