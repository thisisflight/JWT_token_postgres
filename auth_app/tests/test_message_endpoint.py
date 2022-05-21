import datetime
import os
from time import sleep

import jwt
from django.urls import reverse
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APITestCase, APIClient

from auth_app.models import Message, User

SECRET_KEY = os.environ.get('SECRET_KEY')


class MessageTest(APITestCase):
    def setUp(self) -> None:
        self.name = 'name'
        self.password = 'password'
        self.valid_data = {'name': self.name, 'password': self.password}
        self.message = 'message'
        self.last_n_message = 'last 5'
        self.client.post(reverse('signup'), data=self.valid_data)
        self.user = User.objects.filter(name=self.name).first()
        self.bulk_roster = [Message(user=self.user, text=f"text{i}") for i in range(1, 11)]
        self.reverse_keys = [10, 9, 8, 7, 6]

    # проверка создание сообщения залогиненным пользователем и возврат корректного статуса
    def test_successful_creating_a_message_using_cookies(self):
        self.client.post(reverse('login'), data=self.valid_data)
        response = self.client.post(reverse('message'), data={'name': self.name, 'text': self.message})
        self.assertEqual(response.status_code, 201)

    # проверка создания сообщения при помощи предустановленного токена и возврат корректного статуса
    def test_success_status_code_creating_message_using_token(self):
        payload = {
            'name': self.name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        client = APIClient(HTTP_TOKEN=token)
        response = client.post(reverse('message'), data={'name': self.name, 'text': self.message})
        self.assertEqual(response.status_code, 201)

    # проверяем что нельзя создать сообщение с просроченным токеном
    def test_cant_create_message_with_expired_token(self):
        payload = {
            'name': self.name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=1),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        sleep(2)
        client = APIClient(HTTP_TOKEN=token)
        client.post(reverse('message'), data={'name': self.name, 'text': self.message})
        self.assertRaises(jwt.ExpiredSignatureError)

    # проверяем что нельзя создать сообщение по токену по несоответствующему имени
    def test_cant_create_message_with_token_and_invalid_rname(self):
        payload = {
            'name': self.name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        client = APIClient(HTTP_TOKEN=token)
        client.post(reverse('message'), data={'name': 'noname', 'text': self.message})
        self.assertRaises(AuthenticationFailed)

    # проверяем что сообщение успешно создано через токен в заголовках
    def test_successful_create_a_message(self):
        payload = {
            'name': self.name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        client = APIClient(HTTP_TOKEN=token)
        client.post(reverse('message'), data={'name': self.name, 'text': self.message})
        text = Message.objects.first().text
        self.assertEqual(text, self.message)

    # проверяем что по характерному сообщению возвращается список из N сообщений
    def test_get_last_N_of_messages_by_user(self):
        Message.objects.bulk_create(self.bulk_roster)
        self.client.post(reverse('login'), data=self.valid_data)
        response = self.client.post(reverse('message'), data={'name': self.name, 'text': self.last_n_message})
        self.assertEqual(list(response.data.keys()), self.reverse_keys)
