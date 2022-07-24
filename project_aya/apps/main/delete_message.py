import sys, os
import django
sys.path.append('/home/Yerdos/project_aya')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_aya.settings")
django.setup()
from django.conf import settings

import telebot
from datetime import datetime, timezone, timedelta
from main.models import DeleteMessage
from tgbot.functions import check_and_delete_msg

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)

now = timezone.now()
try:
    msgs = DeleteMessage.objects.exclude(deleted=True)
    for msg in msgs:
        utc_time = datetime.fromtimestamp(msg.msg_date, timezone.utc)
        local_time = utc_time.astimezone()
        if local_time >= msg.delete_date:
            check_and_delete_msg(bot, msg.chat_id, msg.msg_id, local_time)
except Message.DoesNotExist:
    print('Для удаления ничего не найдено')
