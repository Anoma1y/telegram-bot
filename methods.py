import config as CONFIG
import requests
import json
from urllib.parse import unquote_plus, unquote, quote, quote_plus

url = 'https://api.telegram.org/bot' + CONFIG.TOKEN + '/'


# getMe - get bots info
def get_me_json():
    response = requests.get(url + 'getMe')
    return response.json()


# getUpdates - get last updates
def get_update_json(offset=100000, timeout=CONFIG.CONNECTION_LOST_TIMEOUT):
    params = {
        'offset': offset,
        'timeout': timeout
    }
    response = requests.get(url + 'getUpdates', data=params)
    return response.json()


# sendMessage - send message by user
def send_message(chat_id, text, disable_web_page_preview=None):
    params = {
        'chat_id': chat_id,
        'text': text
    }
    if disable_web_page_preview is not None:
        params.update({
            'disable_web_page_preview': True
        })
    return requests.post(url + 'sendMessage', params=params)


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

    return requests.post(url + 'sendPhoto', params=params)


# sendMediaGroup - send album
def send_album(chat_id, media):
    params = {
        'chat_id': chat_id,
        'media': json.dumps(media)
    }

    request = requests.post(url + 'sendMediaGroup', params=params)
    print(request.url)

    return requests
