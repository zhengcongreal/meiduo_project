from celery import Celery
import os
# 在发送邮件的异步任务中，我们用到了 Django 的配置文件。
# 所以我们需要修改 celery 的启动文件 main.py。
# 在其中指明 celery 可以读取的 Django 配置文件。

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE']='meiduo_mall.settings.dev'

# 创建对象
celery_app=Celery('meiduo')
# 加载配置文件
celery_app.config_from_object("celery_tasks.config")

# 让 celery_app 自动捕获目标地址下的任务:
# 就是自动捕获 tasks
celery_app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email'])