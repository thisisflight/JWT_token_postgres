import datetime
import os

import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from .serializers import UserSerializer, MessageSerializer
from .models import User, Message
from rest_framework import status


SECRET_KEY = os.environ.get('SECRET_KEY')


class SignUpView(APIView):
    @classmethod
    def post(cls, request) -> Response:
        serializer = UserSerializer(data=request.data)

        # если поля заполнены верно, возвращается статус 201, иначе 400
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    @classmethod
    def post(cls, request) -> Response:
        name = request.data.get('name')
        password = request.data.get('password')
        user = User.objects.filter(name=name).first()

        # если пользователь не зарегистрирован, токен ему выдан не будет
        # если пользователь есть, но пароль неверный, также никакого токена
        if user is None:
            raise AuthenticationFailed('Не найден пользователь с таким именем')
        if not user.check_password(raw_password=password):
            raise AuthenticationFailed('Неправильный пароль')

        # указываем имя, срок действия токена и момент начала действия
        payload = {
            'name': user.name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=3),
            'iat': datetime.datetime.utcnow()
        }

        # хэшируем токен, сохраняем его в куки и возвращаем хэш токена
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        response = Response()
        response.set_cookie(key='token', value=token, httponly=True)
        response.data = {'token': token}
        return response


class MessageView(APIView):
    @classmethod
    def post(cls, request):
        token = request.headers.get('token')
        name = request.data.get('name')
        message = request.data.get('text')

        # первым делом проверяем, есть ли само сообщение
        if message is None:
            raise ValidationError('Отсутствует сообщение')

        # если токен никак не передан ни в запросе, ни в куки, выбрасываем исключение
        if token is None:
            token = request.COOKIES.get('token')
            if token is None:
                raise AuthenticationFailed('Отсутствует токен: возможно вы не авторизованы')

        # проверяем действителен ли токен на момент запроса
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Срок действия токена истек')

        # проверяем, от своего ли имени пользователь отправил сообщение
        user = User.objects.filter(name=payload.get('name')).first()
        if name != user.name:
            raise AuthenticationFailed('Запрещено отправлять сообщения от имени другого пользователя')

        response = Response()

        try:
            # сперва проверяется, не запрашивается ли команда
            # на вывод последних N сообщений
            last, count = message.split()
            count = int(count)
            if last == 'last' and count > 0:
                response.data = dict()
                for message in Message.objects.filter(user=user).all().order_by('-pk')[:count]:
                    response.data[message.pk] = message.text
        except ValueError:
            # в противном случае создаётся сообщение, если параметры переданы верно
            user_id = User.objects.filter(name=name).first().pk
            serializer = MessageSerializer(data={'user': user_id, 'text': message})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response.data = {"status": "Сообщение создано"}
            response.status_code = status.HTTP_201_CREATED

        return response


class LogoutView(APIView):
    @classmethod
    def post(cls, request) -> Response:
        # удаляется токен из куки и пользователю придётся логиниться заново
        response = Response()
        response.delete_cookie('token')
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
