#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, request
import telegram
from telegram.ext import Updater
import methods
import yandere
from time import sleep
import config as CONFIG


app = Flask(__name__)
app.debug = True


global bot
bot = telegram.Bot(token=CONFIG.TOKEN)

URL = '207.154.250.14'


@app.route('/pudge', methods=['POST', 'GET'])
def webhook_handler():
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        try:
            chat_id = update.message.chat.id
            command = update.message.text

            if command:
                handle_cmd(command, chat_id)
            else:
                invalid_cmd(chat_id=chat_id, cmd=command)
        except Exception as e:
            print("type error: " + str(e))
    return 'ok'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('https://%s:443/pudge' % URL, certificate=open('/etc/ssl/server.crt', 'rb'))
    if s:
        print(s)
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route("/")
def hello_world():
    return "Hello World"


unix_time = {
    'minute': 60,
    'hour': 3600,
    'day': 86400,
    'week': 604800,
    'month': 2629743,
    'year': 31556926
}


def get_image():
    pass


# invalid command
def invalid_cmd(chat_id, cmd):
    msg = 'Команда ' + cmd + ' не найдена\n'
    msg += 'Для получения списка доступных команд, напишите /help'
    bot.sendMessage(chat_id=chat_id, text=msg)


# get command list
def get_help_command_list(chat_id):
    help_doc = 'Список доступных команд:\n'
    help_doc += '\t\t/image - Получить картинку\n'
    help_doc += '\t\t/help - Список команд\n'
    bot.sendMessage(chat_id=chat_id, text=help_doc)


def handle_cmd(command, chat_id):

    if command == '/image':
        send_album(chat_id, command)
    elif command == '/help':
        get_help_command_list(chat_id)
    else:
        invalid_cmd(chat_id, command)


def send_album(chat_id, command):
    command = command.split(' ', maxsplit=1)

    json_data = yandere.get_images(page_limit=3, tags=command[1], period_time=unix_time['day'], limit=5)

    for data in json_data:
        bot.sendPhoto(chat_id=chat_id, photo=data['file_url'])


def error():
    pass


# get last updates (message from bot)
def get_last_update_result():
    update_json = methods.get_update_json()  # getUpdate
    result = update_json['result']  # parse json and get result
    last_result = len(result) - 1  # get last result
    return result[last_result]


# get id user
def get_last_chat_id():
    last_result = get_last_update_result()  # get json result
    chat_id = last_result['message']['chat']['id']
    return chat_id

#
# def get_last_commands():
#     last_result = get_last_update_result()
#     text = last_result['message']['text']
#     return text
#
#

#
#

#
#
# # handler command

#
#



# def main():
#     last_update = get_last_update_result()
#     update_id = last_update['update_id']
#
#     while True:
#         new_update = get_last_update_result()
#         new_update_id = new_update['update_id']
#         if new_update_id == update_id:
#
#             last_cmd = get_last_commands()
#             handle_cmd(last_cmd)
#
#             update_id += 1
#         sleep(3)


#if __name__ == '__main__':
#    try:
#        main()
#    except KeyboardInterrupt:
#        exit()
