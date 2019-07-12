from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.views import APIView

from meiduo_mall.libs.captcha.captcha import captcha
from . import constants


class ImageCodeView(APIView):

    def get(self, request,image_code_id):
        text, image = captcha.generate_captcha()

        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return HttpResponse(image,content_type='images/jpg')



