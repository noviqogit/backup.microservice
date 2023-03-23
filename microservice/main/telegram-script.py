from telegram.client import Telegram
from main.selfkeys import api_id, api_hash, phone, SECRET_KEY
import time
from threading import Thread


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
    chat_history = []
    for chat_id in chats:
        thread = Thread(target=parse, args=(chat_id, tg))
        chat_history.append(thread.run())
    for thread in chat_history:
        print(thread)
    tg.stop()


def parse(chat_id, tg):
    message_id = 0
    while True:
        chat_messages = tg.get_chat_history(chat_id, limit=100, from_message_id=message_id)
        chat_messages.wait()
        if chat_messages.error or not chat_messages.update['messages']:
            break
        message_id = chat_messages.update['messages'][0]['id']
        print(chat_id)
        time.sleep(0.1)


if __name__ == '__main__':
    main()
