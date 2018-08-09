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
    'in': {
        'утро': {
            'шесть': 6,
            'семь': 7,
            'восемь': 8,
            'девять': 9,
            'десять': 10,
            'одиннадцать': 11,
            'двенадцать': 12,
            '6': 6,
            '7': 7,
            '8': 8,
            '9': 9,
            '10': 10,
            '11': 11,
            '12': 12
        },
        'день': {
            'час': 13,
            'два': 14,
            'три': 15,
            'четыре': 16,
            'пять': 17,
            'шесть': 18,
            '1': 13,
            '2': 14,
            '3': 15,
            '4': 16,
            '5': 17,
            '6': 18
        },
        'вечер': {
            'шесть': 18,
            'семь': 19,
            'восемь': 20,
            'девять': 21,
            'десять': 22,
            'одиннадцать': 23,
            'двенадцать': 00,
            '6': 18,
            '7': 19,
            '8': 20,
            '9': 21,
            '10': 22,
            '11': 23,
            '12': 0
        },
        'ночь': {
            'двенадцать': 0,
            'час': 1,
            'два': 2,
            'три': 3,
            'четыре': 4,
            'пять': 5,
            'шесть': 6,
            '12': 00,
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
            '6': 6,
        }
    }
}


class Handler:
    def __init__(self):
        pass

    def handle(self, slice, current_time):
        pass

    def is_match(self, val):
        pass

    # Функция для добавления нового времени
    # @params current_time - текущее время
    # @params new_time - массив нового времени [0] - часы, [1] - минуты, [2] - секунды
    # return - новое значение времени (старая дата и новое время), если введеное время меньше,
    # чем текущее и больше чем текущее менее чем на 5 минут, возвращает False
    @staticmethod
    def handle_time(current_time, *new_time):

        d = current_time.date()
        h = int(new_time[0])
        m = int(new_time[1])
        s = int(new_time[2])

        h = h if h >= 0 or h <= 24 else 0
        h = 0 if h == 24 else h
        m = m if m >= 0 or m <= 59 else 0
        s = s if s >= 0 or s <= 59 else 0

        t = datetime.time(h, m, s)
        c_t = datetime.datetime.now()

        # if c_t.time() > t:
        #     return False

        new_time = datetime.datetime.combine(d, t)

        return new_time

    @staticmethod
    def parse_time(available_time_arr, times_of_day=None):
        h = 0
        m = 0
        s = 0

        for t in available_time_arr:

            if re.search('часо?в?', t[1]):
                if times_of_day is None:
                    h = t[0]

                else:
                    if re.search('(вечера?о?м?)', times_of_day):
                        h = time_data['in']['вечер'][t[0]]
                    elif re.search('(утра?о?м?)', times_of_day):
                        h = time_data['in']['утро'][t[0]]
                    elif re.search('(ночи?ь?ю?)', times_of_day):
                        h = time_data['in']['ночь'][t[0]]
                    elif re.search('(дня)', times_of_day):
                        h = time_data['in']['день'][t[0]]

            elif re.search('минуты?', t[1]):
                m = t[0]

            elif re.search('секунды?', t[1]):
                s = t[0]

        return (
            h,
            m,
            s
        )


class InHandler(Handler):
    def handle(self, msg_slice, current_time):
        msg_slice = msg_slice[1:]
        offset = 0

        if re.search('\d\d?', msg_slice[0]) and re.search('(часо?в?|минуты?|секунды?)', msg_slice[1]):
            time_arr = msg_slice[:]
            available_time_arr = []
            times_of_day = None

            for t in range(len(time_arr)):
                if re.search('\d\d?', time_arr[t]) and re.search('(часо?в?|минуты?|секунды?)', time_arr[t + 1]):
                    available_time_arr.append([time_arr[t], time_arr[t + 1]])
                    offset = offset + 2

                elif re.search('((вечера?о?м?)|утра|(ночи?ь?ю?)|дня)', time_arr[t]):
                    times_of_day = time_arr[t]
                    offset = offset + 1

                elif time_arr[t] == 'и':
                    offset = offset + 1

            if len(available_time_arr) != 0:
                (hh, mm, ss) = self.parse_time(available_time_arr, times_of_day)
                current_time = self.handle_time(current_time, hh, mm, ss)

        # if (re.search('\d\d?', msg_slice[0]) or re.search('\d\d?:\d\d', msg_slice[0])) \
        #         and (re.search('(вечера|утра|ночи|дня)', msg_slice[1]) or (re.search('часо?в?', msg_slice[1]) and re.search('(вечера|утра|ночи|дня)', msg_slice[2]))):
        #     pass
            # self.handle_times_of_day(current_time, msg_slice)

        # if re.search('\d\d?', msg_slice[0]) or re.search('\d\d?:\d\d', msg_slice[0]):
        #     current_time = self.handle_times_absolute(current_time, msg_slice)

        else:
            return False

        return {
            'time': current_time,
            'msg': msg_slice[offset:]
        }

    def is_match(self, val):
        return val[0].lower() == 'в'

    def handle_times_of_day(self, current_time, msg):
        split_time = msg[0].split(':')
        print(split_time)
        if re.search('часо?в?', msg[1]):  # msg[1] = <часов> ?

            pass

    def handle_times_absolute(self, current_time, msg):
        split_time = msg[0].split(':') # 1-24

        if len(split_time) != 0:
            hours = split_time[0]
            minutes = split_time[1] if len(split_time) == 2 else 0
            return self.handle_time(current_time, hours, minutes, 0)
        else:
            return False


class AtHandler(Handler):
    def handle(self, slice, current_time):
        print('is_match: через')

        pass

    def is_match(self, val):
        return val[0].lower() == 'через'


class TodayHandler(Handler):
    def handle(self, slice, current_time):

        return {
            'time': datetime.datetime.now(),
            'msg': slice[1:]
        }

    def is_match(self, val):
        return val[0].lower() == 'сегодня'


class Reminder:

    def __init__(self, msg):
        self.msg = msg
        self.msg_arr = []
        self.msg_arr_slice = []
        self.time = None
        self.previous = ''
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

    def set_previous(self, val):
        self.previous = val

    def set_msg_arr_slice(self, msg):
        self.msg_arr_slice = msg

    def start(self):
        self.parse_command()
        self.set_msg_arr_slice(self.msg_arr)
        is_check = True

        while is_check:

            for handle in self.handlers:

                if handle.is_match(val=self.msg_arr_slice):
                    slice = handle.handle(self.msg_arr_slice, self.time)

                    self.set_msg_arr_slice(slice['msg'])
                    self.set_time(slice['time'])

            sleep(1)
            print(self.time)

        print('Done')
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





fuck = Reminder(msg='напомни мне сегодня в 3 час 17 секунд купить что то')
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