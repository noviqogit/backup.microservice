import logging
import time
from microservice.celery import app
from telegram.client import Telegram, AuthorizationState

from main.models import AgregateMessages, Phones, Chats
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('task_log_file.log')
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def get_user_phone_from_database(phone):
    try:
        user_phone = Phones.objects.get(phone=phone)
        return user_phone
    except ObjectDoesNotExist:
        return


def parse(chat, tg):
    last_message_id = 0
    while True:
        chat_messages = tg.get_chat_history(chat.chat_id, from_message_id=last_message_id)
        chat_messages.wait()
        if chat_messages.error:
            break
        messages = chat_messages.update['messages']
        if not messages:
            break
        for message in messages:
            _type = message['content']['@type']
            if _type == 'messageText':
                agregate_text_message(chat, message)
        last_message_id = messages[-1]['id']


def agregate_text_message(chat, message):
    date = message['date']
    text = message['content']['text']['text']

    key = 'user_id' if message['sender_id']['@type'] == 'messageSenderUser' else 'chat_id'
    from_id = message['sender_id'][key]

    logger.info("Agregate message")
    AgregateMessages(chat_id=chat, from_id=from_id, date=date, text=text).save()


@app.task
def get_history(phone, api_id, api_hash, key):
    logger.info("Start")
    tg = Telegram(
        api_id=api_id,
        api_hash=api_hash,
        phone=phone,
        database_encryption_key=key,
    )

    state = tg.login(blocking=False)
    user_phone = None

    for _ in range(120):
        user_phone = get_user_phone_from_database(phone)
        if user_phone:
            break
        time.sleep(1)
    else:
        return

    logger.info("Get code")

    if state == AuthorizationState.WAIT_CODE:
        tg.send_code(user_phone.code)
        state = tg.login(blocking=False)

    if state == AuthorizationState.WAIT_PASSWORD:
        tg.send_password(user_phone.tg_password)
        state = tg.login(blocking=False)

    response = tg.get_chats()
    response.wait()
    chats = response.update['chat_ids']
    for chat_id in chats:
        chat = Chats(phone=user_phone, chat_id=chat_id)
        logger.info("Get chat")
        chat.save()
        parse(chat, tg)
    tg.stop()
