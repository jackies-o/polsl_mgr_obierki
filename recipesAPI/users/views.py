from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse, HttpResponse, Http404
from rest_framework import status, serializers
from rest_framework.generics import GenericAPIView
from django.shortcuts import render
import json
import django.core

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import UserSerializer, LoginSerializer

from django.conf import settings
from django.contrib import auth
import jwt


class RegisterView(GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {'isCreated': True}
            return JsonResponse(data, status=status.HTTP_201_CREATED)

        data = {'isCreated': True, 'errorMessage': serializer.errors}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        data = request.data
        username = data.get('username', '')
        password = data.get('password', '')
        user = auth.authenticate(username=username, password=password)

        if user:
            auth_token = jwt.encode(
                {'username': user.username}, settings.JWT_SECRET_KEY, algorithm="HS256")

            serializer = UserSerializer(user)

            data = {'id': user.id, 'token': auth_token}

            return JsonResponse(data, status=status.HTTP_200_OK)

            # SEND RES
        return JsonResponse({'errorMessage': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserDetail(APIView):
    """
    Retrieve, update or delete a user instance.
    """

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        user_serializer = UserSerializer(user)
        return JsonResponse({'id': user_serializer.id, 'username': user_serializer.username}, safe=False)

    def put(self, request, pk, format=None):
        try:
            user = self.get_object(pk)
        except Http404 as http404Er:
            return JsonResponse({'isUpdated': False, 'errorMessage': http404Er}, safe=False,
                                status=status.HTTP_404_NOT_FOUND)
        user_serializer = UserSerializer(user, data=request.data)
        try:
            if user_serializer.is_valid(raise_exception=True):
                user_serializer.save()
                return JsonResponse({'isUpdated': True, 'errorMessage': ""}, safe=False, status=status.HTTP_200_OK)
        except serializers.ValidationError as valEr:
            return JsonResponse({'isUpdated': False, 'errorMessage': valEr.detail}, safe=False,
                                status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        try:
            user = self.get_object(pk)
        except Http404 as http404Er:
            return JsonResponse({'isUpdated': False, 'errorMessage': http404Er}, safe=False,
                                status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserList(APIView):
    """
    Create or get user instance.
    """

    def user_exists_by_name(self, name):
        return User.objects.filter(username=name).exists()

    def get(self, request, format=None):
        users_objects = User.objects.all()
        data = django.core.serializers.serialize('json', users_objects)
        return HttpResponse(data, content_type="application/json")

    def post(self, request, pk, format=None):
        user_serializer = UserSerializer(data=request.data)
        try:
            if user_serializer.is_valid(raise_exception=True):
                if not self.user_exists_by_name(user_serializer.validated_data['username']):
                    user_serializer.save()
                    return JsonResponse({'isCreated': True, 'errorMessage': ""}, safe=False,
                                        status=status.HTTP_201_CREATED)
                return JsonResponse({'isCreated': False, 'errorMessage': user_serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as valEr:
            return JsonResponse({'isCreated': False, 'errorMessage': valEr.detail}, safe=False,
                                status=status.HTTP_400_BAD_REQUEST)
