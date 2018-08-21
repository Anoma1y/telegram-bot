#!/usr/bin/python
# -*- coding: utf-8 -*-

import telegram
import re
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, run_async
# import postgresql
import yandere
from reminder import Reminder
import config as CONFIG
import datetime
from calendar import monthrange
from time import *
from db import Queries

# db = postgresql.open('pq://' + CONFIG.DB_USERNAME + ':' + CONFIG.DB_PASSWORD + '@' + CONFIG.DB_HOST + ':' + str(CONFIG.DB_PORT) + '/' + CONFIG.DB_NAME)

unix_time = {
    'minute': 60,
    'hour': 3600,
    'day': 86400,
    'week': 604800,
    'month': 2629743,
    'year': 31556926
}


# invalid command
def invalid_cmd(bot, update):
    msg = 'Команда ' + update.message.text + ' не найдена\n'
    msg += 'Для получения списка доступных команд, напишите /help'

    bot.sendMessage(chat_id=update.message.chat_id, text=msg)


# get command list
def get_help_command_list(bot, update):
    help_doc = 'Список доступных команд:\n'
    help_doc += '\t\t/image {{имя тега}} - Получить последние картинки за 1 неделю, {{имя тега}} - картинки по тегу\n'
    help_doc += '\t\t/tags {{имя тега}} - Получить все популярные теги, {{имя тега}} - поиск по тегу\n'
    help_doc += '\t\t/help - Список команд\n'
    bot.sendMessage(chat_id=update.message.chat_id, text=help_doc)


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


def get_params_cmd(update):
    cmd = update.message.text.split(' ', maxsplit=1)

    if len(cmd) <= 1:
        param = ''
    else:
        param = cmd[1]

    return param


def send_album(bot, update):
    tags = get_params_cmd(update)

    json_data = yandere.get_images(page_limit=3, tags=tags, period_time=unix_time['week'], limit=5)

    if len(json_data) == 0:
        bot.sendMessage(chat_id=update.message.chat_id, text='Изображения не найдены')

    for data in json_data:
        bot.sendPhoto(chat_id=update.message.chat_id, photo=data['file_url'])


def send_tags(bot, update):
    tag_name = get_params_cmd(update)

    tags_list = yandere.get_available_tags(tag_name)

    if len(tags_list) > 0:
        bot.sendMessage(chat_id=update.message.chat_id, text=tags_list)
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text='Теги не найдены')


def error():
    pass


def check_reminder(msg):
    remind_word = 'напомни мне'
    msg = re.sub('\s+', ' ', msg)

    if re.search(remind_word, msg.lower()) or re.search('^что\s', msg.strip()):
        return True

    return False


def text_message(msg):
    response = msg
    if check_reminder(response):
        try:
            reminder = Reminder(msg=response)
            (msg, time) = reminder.start()

            query = Queries()
            query.insert_remind(21012454, msg, time.strftime("%Y-%m-%d %H:%M:%S"))

            print('Напоминание создано')
        except Exception as err:
            err = str(err)
            print(err)
    else:
        print('Hi')


text_message('напомни мне через 15 минут сходить на встречу')


# def text_message(bot, update):
#     response = update.message.text
#     if check_reminder(response):
#         try:
#             reminder = Reminder(msg=response)
#             (msg, time) = reminder.start()
#             query = Queries()
#             query.insert_remind(update.message.chat_id, msg, time)

            # bot.send_message(chat_id=update.message.chat_id, text='Напоминание создано')
        # except Exception as err:
        #     bot.send_message(chat_id=update.message.chat_id, text=str(err))
#


# query = Queries()
# query.insert_remind(14221214234234, 'hell', 'now()')
# print(query.get_remind())
# print(query.get_remind_single(12))
# print(query.get_remind_upcoming())
# reminder = Reminder(msg='напомни мне через 10 минут встреча с кем то там')
# reminder = Reminder(msg='напомни мне сегодня в 18 часов и 35 минут встреча с кем то там и где то там')
# (msg, time) = reminder.start()
# print(msg, time)

# def text_message(bot, update):
#     response = 'Получил Ваше сообщение: ' + update.message.text
#     bot.send_message(chat_id=update.message.chat_id, text=response)


# def set_notification(bot, update):
#     ins = db.prepare("INSERT INTO reminder (user_id, creator_id, message, notify_at) VALUES (1, 2, '1', 'now()')")
#
#     bot.send_message(chat_id=update.message.chat_id, text='Добавлено')


# updater = Updater(token=CONFIG.TOKEN)
# dispatcher = updater.dispatcher

# @run_async
# def starter(bot, update):
#     # print('Hui start')
#     while True:
#         pass
#         # get_emp_with_salary_lt = db.query("SELECT message FROM reminder WHERE notify_at > now()")
#
#         # print(get_emp_with_salary_lt)
#         # sleep(2)


# def main():
#     try:
#         text_message_handler = MessageHandler(Filters.text, text_message)
#         # start_command_handler = CommandHandler('start', starter)
#         tags_command_handler = CommandHandler('tags', send_tags)
#         image_command_handler = CommandHandler('image', send_album)
#         help_command_handler = CommandHandler('help', get_help_command_list)
#         # set_command_handler = CommandHandler('set', set_notification)
#         # dispatcher.add_handler(start_command_handler)
#         dispatcher.add_handler(tags_command_handler)
#         dispatcher.add_handler(image_command_handler)
#         dispatcher.add_handler(help_command_handler)
#         # dispatcher.add_handler(set_command_handler)
#         dispatcher.add_handler(text_message_handler)
#
#         updater.start_polling(clean=True)
#
#         updater.idle()
#     except Exception as e:
#         print("type error: " + str(e))
#
#
# if __name__ == '__main__':
#     try:
#         main()
#     except KeyboardInterrupt:
#         exit()