#!/usr/bin/python
# -*- coding: utf-8 -*-
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, run_async
import methods
import yandere
import config as CONFIG
from time import sleep



# app = Flask(__name__)
# app.debug = True
#
#
# global bot
# bot = telegram.Bot(token=CONFIG.TOKEN)
#
# URL = '207.154.250.14'
#
#
# @app.route('/pudge', methods=['POST', 'GET'])
# def webhook_handler():
#     if request.method == "POST":
#         update = telegram.Update.de_json(request.get_json(force=True), bot)
#         try:
#             chat_id = update.message.chat.id
#             command = update.message.text
#
#             if command:
#                 handle_cmd(command, chat_id)
#             else:
#                 invalid_cmd(chat_id=chat_id, cmd=command)
#         except Exception as e:
#             print("type error: " + str(e))
#     return 'ok'


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
    # bot.sendMessage(chat_id=chat_id, text=msg)


# get command list
def get_help_command_list(chat_id):
    help_doc = 'Список доступных команд:\n'
    help_doc += '\t\t/image {{tag}} - Получить последние картинки за 1 неделю\n'
    help_doc += '\t\t/tags - Получить все популярные теги\n'
    help_doc += '\t\t/help - Список команд\n'
    # bot.sendMessage(chat_id=chat_id, text=help_doc)


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


def send_album(bot, update):
    tags = update.message.text.split(' ', maxsplit=1)

    if len(tags) <= 1:
        tags = None

    json_data = yandere.get_images(page_limit=3, tags=tags[1], period_time=unix_time['week'], limit=5)

    for data in json_data:
        pass
        bot.sendPhoto(chat_id=update.message.chat_id, photo=data['file_url'])


def send_tags(bot, update):
    tags_list = yandere.get_available_tags()

    if len(tags_list) > 0:
        pass
        bot.sendMessage(chat_id=update.message.chat_id, text=tags_list)


def error():
    pass


def startCommand(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


def textMessage(bot, update):
    response = 'Получил Ваше сообщение: ' + update.message.text
    bot.send_message(chat_id=update.message.chat_id, text=response)


updater = Updater(token=CONFIG.TOKEN)
dispatcher = updater.dispatcher


def gg_lol(bot, update):
    while True:
        print('Hui')
        sleep(2)


@run_async
def starter(bot, update):
    gg_lol(bot, update)


def main():
    try:
        text_message_handler = MessageHandler(Filters.text, textMessage)
        start_command_handler = CommandHandler('start', starter)
        tags_command_handler = CommandHandler('tags', send_tags)
        image_command_handler = CommandHandler('image', send_album)

        dispatcher.add_handler(start_command_handler)
        dispatcher.add_handler(tags_command_handler)
        dispatcher.add_handler(image_command_handler)
        dispatcher.add_handler(text_message_handler)

        updater.start_polling(clean=True)

        updater.idle()
    except Exception as e:
        print("type error: " + str(e))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()