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
                  'offset': 0,
                  'limit': 99,
                  'only_local': False}
        i = 0
        while True:
            params['from_message_id'] = i
            result = tg.call_method('getChatHistory', params)
            if result.error:
                break
            result.wait()
            print(result.update)
            i += 1

    tg.stop()


if __name__ == '__main__':
    main()
