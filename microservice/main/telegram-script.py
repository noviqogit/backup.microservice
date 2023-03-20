from telegram.client import Telegram
from main.selfkeys import api_id, api_hash, phone, SECRET_KEY


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
        params = {'chat_id': chat_id,
                  'from_message_id': 0,
                  # 'offset': -1,
                  'limit': 10}
        result = tg.call_method('getChatHistory', params)
        result.wait()
        print(result.update['messages'][0])
    tg.stop()


if __name__ == '__main__':
    main()
