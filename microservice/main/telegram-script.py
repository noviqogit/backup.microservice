from telegram.client import Telegram
from main.selfkeys import api_id, api_hash, phone, SECRET_KEY
from .models import Messages


def main():
    tg = Telegram(
        api_id=api_id,
        api_hash=api_hash,
        phone=phone,
        database_encryption_key=SECRET_KEY
    )
    tg.login()

    response = tg.get_chats()
    response.wait()
    chats = response.update['chat_ids']
    for chat_id in chats:
        parse(chat_id, tg)
    tg.stop()


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
                pass
                # Messages(chat_id=chat_id, from_id=None)
            # if _type == 'messagePhoto':
            #     print(message['content']['caption'])
            # if _type == 'messageDocument':
            #     print(message)
        last_message_id = messages[-1]['id']


if __name__ == '__main__':
    main()
