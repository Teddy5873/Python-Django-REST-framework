from django.shortcuts import render

# Create your views here.


from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users import serializers
from users.models import User



class UserView(CreateAPIView):
    serializer_class = serializers.CreateUserSerializer


class UsernameCountView(APIView):
    def get(self,request,username):
        count = User.objects.filter(username=username).count()
        data = {
            'username':username,
            'count':count
        }
        return Response(data)


class MobileCountView(APIView):

    def get(self, request, mobile):

        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)