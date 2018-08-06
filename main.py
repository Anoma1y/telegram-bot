#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, request
import telegram
from telegram.ext import Updater
import methods
import yandere
import asyncio
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
    help_doc += '\t\t/image {{tag}} - Получить последние картинки за 1 неделю\n'
    help_doc += '\t\t/tags - Получить все популярные теги\n'
    help_doc += '\t\t/help - Список команд\n'
    bot.sendMessage(chat_id=chat_id, text=help_doc)


def handle_cmd(command, chat_id):
    main_command = command.split(' ', maxsplit=1)[0]

    if main_command == '/image':
        send_album(chat_id, command)
    elif main_command == '/tags':
        send_tags(chat_id)
    elif main_command == '/help':
        get_help_command_list(chat_id)
    else:
        invalid_cmd(chat_id, main_command)


def send_album(chat_id, command):
    tags = command.split(' ', maxsplit=1)

    if len(tags) <= 1:
        tags = None

    json_data = yandere.get_images(page_limit=3, tags=tags[1], period_time=unix_time['week'], limit=5)

    for data in json_data:
        bot.sendPhoto(chat_id=chat_id, photo=data['file_url'])


def send_tags(chat_id):
    tags_list = yandere.get_available_tags()

    if len(tags_list) > 0:
        bot.sendMessage(chat_id=chat_id, text=tags_list)


def error():
    pass
