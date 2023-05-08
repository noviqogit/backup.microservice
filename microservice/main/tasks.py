import time
from celery import shared_task
from telegram.client import Telegram, AuthorizationState

from main.models import AgregateMessages, Phones
from django.core.exceptions import ObjectDoesNotExist


def get_user_from_database(phone):
    try:
        user = Phones.objects.get(phone=phone)
        return user
    except ObjectDoesNotExist:
        return


def parse(chat_id, tg):
    last_message_id = 0
    while True:
        chat_messages = tg.get_chat_history(chat_id, from_message_id=last_message_id)
        chat_messages.wait()
        if chat_messages.error:
            break
        messages = chat_messages.update['messages']
        if not messages:
            break
        for message in messages:
            _type = message['content']['@type']
            if _type == 'messageText':
                agregate_text_message(message)
        last_message_id = messages[-1]['id']


def agregate_text_message(message):
    chat_id = message['chat_id']
    date = message['date']
    text = message['content']['text']['text']

    key = 'user_id' if message['sender_id']['@type'] == 'messageSenderUser' else 'chat_id'
    from_id = message['sender_id'][key]

    AgregateMessages(chat_id=chat_id, from_id=from_id, date=date, text=text)


@shared_task()
def get_history(phone, api_id, api_hash, key):
    tg = Telegram(
        api_id=api_id,
        api_hash=api_hash,
        phone=phone,
        database_encryption_key=key,
    )

    state = tg.login(blocking=False)
    user = None

    for _ in range(120):
        user = get_user_from_database(phone)
        if user:
            break
    else:
        return

    if state == AuthorizationState.WAIT_CODE:
        tg.send_code(user.code)
        state = tg.login(blocking=False)

    if state == AuthorizationState.WAIT_PASSWORD:
        tg.send_password(user.password)
        state = tg.login(blocking=False)

    response = tg.get_chats()
    response.wait()
    chats = response.update['chat_ids']
    for chat_id in chats:
        parse(chat_id, tg)
    tg.stop()
