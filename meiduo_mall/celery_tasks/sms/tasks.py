from celery_tasks.main import celery_app
from celery_tasks.sms.yuntongxun.ccp_sms import CCP
# 我们需要使用celery提供的装饰器去装饰该函数，让celery可以识别该函数
@celery_app.task(name="ccp_send_sms_code")
def ccp_send_sms_code(mobile,sms_code):
    result=CCP().send_template_sms(mobile, [sms_code, 5], 1)
    return result