import random

from django.test import TestCase

# Create your tests here.
random_num = random.randint(0, 999999)
# 8. 保存短信验证码
sms_code = ("%06d" % random_num)
print(sms_code)