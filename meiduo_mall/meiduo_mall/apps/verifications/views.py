import random
from django.http.response import HttpResponse
from django.shortcuts import render
from meiduo_mall.utils.yuntongxun.sms import CCP
# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView

from meiduo_mall.libs.captcha.captcha import captcha
from verifications.serializers import ImageCodeCheckSerializer
from . import constants
from celery_tasks.sms.tasks import send_sms_code

class ImageCodeView(APIView):

    def get(self, request,image_code_id):
        text, image = captcha.generate_captcha()

        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return HttpResponse(image,content_type='images/jpg')


class SMSCodeView(GenericAPIView):
    serializer_class = ImageCodeCheckSerializer

    def get(self,request,mobile):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        sms_code = "%06d" % random.randint(0, 999999)
        print(sms_code)

        redis_conn = get_redis_connection('verify_codes')
        p1 = redis_conn.pipeline()
        p1.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        p1.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        p1.execute()

        # expires = str(constants.SMS_CODE_REDIS_EXPIRES // 60)
        # ccp = CCP()
        # ccp.send_template_sms(mobile, [sms_code, expires], constants.SMS_CODE_TEMP_ID)
        #
        # return Response({"message": "OK"})
        expires = constants.SMS_CODE_REDIS_EXPIRES // 60
        send_sms_code.delay(mobile, sms_code, expires, constants.SMS_CODE_TEMP_ID)

        return Response({'message': 'OK'})








