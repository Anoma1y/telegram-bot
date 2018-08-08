#!/usr/bin/python
# -*- coding: utf-8 -*-
import telegram
import re
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, run_async
import logging
import postgresql
import yandere
import config as CONFIG
import datetime
from time import *

db = postgresql.open('pq://' + CONFIG.DB_USERNAME + ':' + CONFIG.DB_PASSWORD + '@' + CONFIG.DB_HOST + ':' + str(CONFIG.DB_PORT) + '/' + CONFIG.DB_NAME)

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


remind1 = 'напомни мне в июле 2019 сделать таск'
remind3 = 'напомни мне через 1 час встреча с кем то там'
remind4 = 'напомни мне через 4 дня 2 часа 5 минут и 10 секунд пойти погулять'
remind5 = 'напомни мне 14 августа 2018 в 10 часов сходить купить поесть'

remind2 = 'напомни мне сегодня в 10 вечера купить что то'

time_data = {
    'at': ['утра', 'дня', 'вечера']
}


class Handler:
    def __init__(self):
        pass

    def handle(self, slice):
        pass

    def is_match(self, val):
        pass


class InHandler(Handler):
    def handle(self, slice):
        pass

    def is_match(self, val):
        return val[0].lower() == 'в'


class AtHandler(Handler):
    def handle(self, slice):
        pass

    def is_match(self, val):
        return val[0].lower() == 'через'


class TodayHandler(Handler):
    def handle(self, slice):
        return (
            time(),
            slice[1:]
        )

    def is_match(self, val):
        return val[0].lower() == 'сегодня'


class Reminder:

    def __init__(self, msg):
        self.msg = msg
        self.msg_arr = []
        self.msg_arr_slice = []
        self.time = None
        self.date = {
            'is_today': False,
            'is_tommorow': False
        }
        self.handlers = [
            InHandler(),
            AtHandler(),
            TodayHandler()
        ]

    def parse_command(self):
        remind_word = 'напомни мне'
        msg = re.sub('\s+', ' ', self.msg)

        if re.search(remind_word, msg.lower()):
            if re.search('^что\s', msg[len(remind_word):].strip()):
                self.set_msg_arr(msg[(len(remind_word) + 5):].strip().split(' '))
            self.set_msg_arr(msg[len(remind_word):].strip().split(' '))
        else:
            self.set_msg_arr('')

    def set_msg_arr(self, msg):
        self.msg_arr = msg

    def set_time(self, time):
        self.time = time

    def set_msg_arr_slice(self, msg):
        self.msg_arr_slice = msg

    def start(self):
        self.parse_command()
        self.set_msg_arr_slice(self.msg_arr)
        is_check = True

        while is_check:

            for handle in self.handlers:
                if handle.is_match(val=self.msg_arr):
                    slice = handle.handle(self.msg_arr_slice)

                    is_check = False
                    # self.set_msg_arr_slice(slice)


        # for i in range(len(self.msg_arr)):
        #     for handle in self.handlers:
        #         if handle.is_match(val=self.msg_arr):

            # msg = self.msg_arr[i]
            # self.handlers
            # print(self.msg_arr)
        #
        #     if (i == 0) and (msg == 'сегодня'):
        #         self._today()
        #
        #     if i != 0 and msg == 'в':
        #
        #         if re.search('\d', self.msg_arr[i + 1]):
        #             digit_time = self.msg_arr[i + 1]
        #
        #             if self.msg_arr[i + 2] in time_data['at']:
        #
        #                 day_of_time = self.msg_arr[i + 2]
        #                 print(digit_time, day_of_time)
        #
        #     elif msg == 'через':
        #         self._in()





fuck = Reminder(msg='напомни мне сегодня в 10 вечера купить что то')
# fuck = Reminder(msg='напомни мне через 3 часа купить что то')
fuck.start()
# fuck.set_msg_arr()
# fuck.print_msg()

# day = re.search('(\d+)(\s+)?(секунды?|минуты?|час|день|дней|дня|недел[иья]|месяца?|года?|лет)(\s+)?[и,]?(\s+)?', '1 час и 10 минут')

"hello {name} today is {weekday}".format(
    name="john",
    weekday="sunday"
)

# print(day)


def text_message(bot, update):
    response = 'Получил Ваше сообщение: ' + update.message.text
    bot.send_message(chat_id=update.message.chat_id, text=response)


def set_notification(bot, update):
    ins = db.prepare("INSERT INTO reminder (user_id, creator_id, message, notify_at) VALUES (24787878232, 545777888833, 'Тестовый с питона', 'now()')")

    bot.send_message(chat_id=update.message.chat_id, text='Добавлено')


updater = Updater(token=CONFIG.TOKEN)
dispatcher = updater.dispatcher


@run_async
def starter(bot, update):
    print('Hui start')
    while True:
        pass
        get_emp_with_salary_lt = db.query("SELECT message FROM reminder WHERE notify_at > now()")

        print(get_emp_with_salary_lt)
        sleep(2)


def main():
    try:
        text_message_handler = MessageHandler(Filters.text, text_message)
        start_command_handler = CommandHandler('start', starter)
        tags_command_handler = CommandHandler('tags', send_tags)
        image_command_handler = CommandHandler('image', send_album)
        help_command_handler = CommandHandler('help', get_help_command_list)
        set_command_handler = CommandHandler('set', set_notification)

        dispatcher.add_handler(start_command_handler)
        dispatcher.add_handler(tags_command_handler)
        dispatcher.add_handler(image_command_handler)
        dispatcher.add_handler(help_command_handler)
        dispatcher.add_handler(set_command_handler)
        dispatcher.add_handler(text_message_handler)
        # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        updater.start_polling(clean=True)

        updater.idle()
    except Exception as e:
        print("type error: " + str(e))

#
# if __name__ == '__main__':
#     try:
#         main()
#     except KeyboardInterrupt:
#         exit()