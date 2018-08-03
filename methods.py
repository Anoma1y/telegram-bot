import config as CONFIG
import requests

url = 'https://api.telegram.org/bot' + CONFIG.token + '/'


# getMe - get bots info
def get_me_json():
    response = requests.get(url + 'getMe')
    return response.json()


# getUpdates - get last updates
def get_update_json():
    response = requests.get(url + 'getUpdates')
    return response.json()


# sendMessage - send message by user
def send_message(chat_id, text):
    params = {
        'chat_id': chat_id,
        'text': text
    }
    return requests.post(url + 'sendMessage', data=params)


# sendPhoto - send photo
def send_photo(chat_id, photo, caption=None):
    params = {
        'chat_id': chat_id,
        'photo': photo
    }

    if caption is not None:
        params.update({
            'caption': 'test'
        })

    return requests.post(url + 'sendPhoto', data=params)

