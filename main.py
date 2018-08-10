#!/usr/bin/python
# -*- coding: utf-8 -*-
import telegram
import re
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, run_async
import logging
# import postgresql
import yandere
import config as CONFIG
import datetime
from calendar import monthrange
from time import *

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

    # Статический метод для добавления нового времени
    # @params current_time - текущее время ------------------
    # @params new_time - массив нового времени [0] - часы, [1] - минуты, [2] - секунды
    # return - новое значение времени (старая дата и новое время), если введеное время меньше,
    # чем текущее и больше чем текущее менее чем на 5 минут, возвращает False
    @staticmethod
    def handle_time(*new_time):

        hour = int(new_time[0])
        minute = int(new_time[1])
        second = int(new_time[2])

        hour = hour if hour >= 0 or hour <= 24 else 0
        hour = 0 if hour == 24 else hour
        minute = minute if minute >= 0 or minute <= 59 else 0
        second = second if second >= 0 or second <= 59 else 0

        t = datetime.time(hour, minute, second)

        return t

    @staticmethod
    def handle_date(*new_date):
        day = int(new_date[0])
        month = int(new_date[1])
        year = int(new_date[2])

        c_d = datetime.datetime.now()

        if (day >= 1 and day <= monthrange(year, month)[1]) is False:
            return False

        elif (month >= 1 and month <= 12) is False:
            return False

        elif year < int(c_d.date().year):
            return False

        d = datetime.date(year, month, day)

        if d < c_d.date():
            return False

        return d

    # Метод для добавления нового времени
    # @params d - дата в раскрытом формате (d.date())
    # @params t - время в раскрытом формате (t.time())
    # return - новое значение времени datetime
    @staticmethod
    def set_time(d, t):
        return datetime.datetime.combine(d, t)

    # Метод записывающий результат выполнения
    # @params new_time - новое время, в формате datetime.datetime
    # @params msg - новый, обрезанный массив
    # @params err - ошибка
    # return - кортеж значений
    @staticmethod
    def set_result(new_time=None, msg='', err=''):
        return (
            new_time,
            msg,
            err
        )

    # Метод для проверки времени
    # @params new_time - проверяемое время
    # return - True, иначе если ошибка, вернет объект с указанием ошибки
    @staticmethod
    def check_time(new_time):  # todo сделать проверку времени больше, чем текущее на 5-15 минут
        c_t = datetime.datetime.now()

        if c_t > new_time:
            return 'Указаное время меньше текущего'

        return True

    # Метод которые возвщатает время в зависимости от модификатора времени (утром, днем, вечером, ночью)
    # @params times_of_day - модификатор времени (по дефолту равен None)
    # @params hours - часы
    # return - новое значение времени (h - часы, m - минуты, s - секунды)
    @staticmethod
    def handle_set_time_times_of_day(times_of_day, hours):
        h = hours

        if re.search('(вечера?о?м?)', times_of_day):
            h = time_data['in']['вечер'][hours]

        elif re.search('(утра?о?м?)', times_of_day):
            h = time_data['in']['утро'][hours]

        elif re.search('(ночи?ь?ю?)', times_of_day):
            h = time_data['in']['ночь'][hours]

        elif re.search('(дня)', times_of_day):
            h = time_data['in']['день'][hours]

        return h

    # Статический метод для парсинга нового времени в виде массива ['3 часа', '10 минут']
    # @params available_time_arr - массив массивов времени [[\d\, \str\]]
    # @params times_of_day - модификатор времени (по дефолту равен None)
    # return - новое значение времени (h - часы, m - минуты, s - секунды)
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
                    h = Handler.handle_set_time_times_of_day(times_of_day, t[0])

            elif re.search('минуты?', t[1]):
                m = t[0]

            elif re.search('секунды?', t[1]):
                s = t[0]

        return (
            h,
            m,
            s
        )

    # Метод для парсинга времени в текстовом формате (1 час, 5 минут и тп)
    # @params msg_slice - массив сообщения
    # @params current_time - текущее время, созданное в классе Reminder
    # return - кортеж: новое значение времени (h - часы, m - минуты, s - секунды) и обрезанное сообщение
    @staticmethod
    def parse_times_from_slice(msg_slice, current_time):
        offset = 0
        time_arr = msg_slice[:]
        available_time_arr = []
        times_of_day = None  # модификатор времени (утра, дня, вечера, ночи)
        new_current_datetime = None
        err = ''

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
            (hh, mm, ss) = Handler.parse_time(available_time_arr, times_of_day)
            new_time = Handler.handle_time(hh, mm, ss)
            new_current_datetime = Handler.set_time(current_time.date(), new_time)
            check_time = Handler.check_time(new_current_datetime)

            if check_time is not True:
                (err) = check_time  # вывод ошибки если указанное время меньше текущего

        return (
            new_current_datetime,
            msg_slice[offset:],
            err
        )

    @staticmethod
    def parse_absolute_times_from_slice(msg_slice, current_time):
        offset = 1
        time_arr = msg_slice[0].split(':')
        times_of_day = None  # модификатор времени (утра, дня, вечера, ночи)

        if re.search('((вечера?о?м?)|утра|(ночи?ь?ю?)|дня)', msg_slice[1]):
            times_of_day = msg_slice[1]
            offset = offset + 1

        hh = time_arr[0] if time_arr[0] in time_arr else 0

        if times_of_day is not None:
            hh = Handler.handle_set_time_times_of_day(times_of_day, hh)

        mm = time_arr[1] if len(time_arr) >= 2 else 0
        ss = time_arr[2] if len(time_arr) == 3 else 0

        new_time = Handler.handle_time(hh, mm, ss)
        new_current_datetime = Handler.set_time(current_time.date(), new_time)

        # c_t = datetime.datetime.now()
        # if c_t > td:
        #     return False

        return (
            new_current_datetime,
            msg_slice[offset:],
            ''
        )


class AtHandler(Handler):
    def handle(self, msg_slice, current_time):
        msg_slice = msg_slice[1:]

        if re.search('\d\d?', msg_slice[0]) and re.search('(часо?в?|минуты?|секунды?)', msg_slice[1]):
            (new_current_time, new_msg_slice, err) = self.parse_times_from_slice(msg_slice, current_time)

        elif re.search('\d\d?', msg_slice[0]) or re.search('\d\d?:\d\d', msg_slice[0]):
            (new_current_time, new_msg_slice, err) = self.parse_absolute_times_from_slice(msg_slice, current_time)

        else:
            return False

        return (
            new_current_time,
            new_msg_slice,
            err
        )

    def is_match(self, val):
        return val[0].lower() == 'в'

    def handle_times_absolute(self, current_time, msg):
        split_time = msg[0].split(':')

        if len(split_time) != 0:
            hours = split_time[0]
            minutes = split_time[1] if len(split_time) == 2 else 0
            return self.handle_time(current_time, hours, minutes, 0)

        else:
            return False


class InHandler(Handler):
    def handle(self, slice, current_time):
        print('is_match: через')

        pass

    def is_match(self, val):
        return val[0].lower() == 'через'


class TodayHandler(Handler):
    def handle(self, slice, current_time):
        today = datetime.datetime.now()
        today_date = today.date()

        if current_time is not None:
            today = Handler.set_time(today_date, current_time.time())

        return (
            today,
            slice[1:],
            ''
        )

    def is_match(self, val):
        return val[0].lower() == 'сегодня'


class TomorrowHandler(Handler):
    def __init__(self):
        super().__init__()
        self._days = {
            'завтра': 1,
            'послезавтра': 2,
            'послепослезавтра': 3,
        }
        self._match = 'завтра'

    @property
    def days(self):
        return self._days

    @property
    def match(self):
        return self._match

    @match.setter
    def match(self, val):
        self._match = val

    def handle(self, slice, current_time):
        today = datetime.datetime.now()
        tomorrow = today + datetime.timedelta(days=self.days[self.match])
        tomorrow_date = tomorrow.date()

        if current_time is not None:
            tomorrow = Handler.set_time(tomorrow_date, current_time.time())

        return (
            tomorrow,
            slice[1:],
            ''
        )

    def is_match(self, val):
        if val[0].lower() in self.days:
            self.match = val[0].lower()

            if val[0].lower() == self.match:
                return True

        return False


class Reminder:

    def __init__(self, msg):
        self._msg = msg
        self._msg_arr = []
        self._msg_arr_slice = []
        self._time = None

        self.handlers = [
            InHandler(),
            AtHandler(),
            TodayHandler(),
            TomorrowHandler()
        ]

    @property
    def msg(self):
        return self._msg

    @property
    def msg_arr(self):
        return self._msg_arr

    @property
    def time(self):
        return self._time

    @property
    def msg_arr_slice(self):
        return self._msg_arr_slice

    @msg_arr.setter
    def msg_arr(self, value):
        self._msg_arr = value

    @time.setter
    def time(self, value):
        self._time = value

    @msg_arr_slice.setter
    def msg_arr_slice(self, value):
        self._msg_arr_slice = value

    # Метод поиска команды для запуска парсера
    def parse_command(self):
        remind_word = 'напомни мне'
        msg = re.sub('\s+', ' ', self.msg)

        if re.search(remind_word, msg.lower()):

            if re.search('^что\s', msg[len(remind_word):].strip()):
                self.msg_arr = msg[(len(remind_word) + 5):].strip().split(' ')

            self.msg_arr = msg[len(remind_word):].strip().split(' ')

        else:
            self.msg_arr = ''

    def start(self):
        self.parse_command()
        self.msg_arr_slice = self.msg_arr
        is_check = True

        while is_check:

            for handle in self.handlers:

                if handle.is_match(val=self.msg_arr_slice):

                    ( new_current_time, new_msg_slice, err ) = handle.handle(self.msg_arr_slice, self.time)

                    if len(err) != 0:
                        print(err)
                        is_check = False

                    self.msg_arr_slice = new_msg_slice
                    self.time = new_current_time

                elif len(self.msg_arr_slice) == 0:
                    is_check = False

            sleep(1)
            print('Reminder time: ', self.time)

        print('Done')


# reminder = Reminder(msg='напомни мне завтра в 5 часов 25 минут дня купить дилдак по скидке')
reminder = Reminder(msg='напомни мне сегодня в 5 часов 3 минуты 17 секунд ночи купить дилдак по скидке')

reminder.start()

"hello {name} today is {weekday}".format(
    name="john",
    weekday="sunday"
)


# def text_message(bot, update):
#     response = 'Получил Ваше сообщение: ' + update.message.text
#     bot.send_message(chat_id=update.message.chat_id, text=response)
#
#
# def set_notification(bot, update):
#     ins = db.prepare("INSERT INTO reminder (user_id, creator_id, message, notify_at) VALUES (24787878232, 545777888833, 'Тестовый с питона', 'now()')")
#
#     bot.send_message(chat_id=update.message.chat_id, text='Добавлено')
#
#
# updater = Updater(token=CONFIG.TOKEN)
# dispatcher = updater.dispatcher
#
#
# @run_async
# def starter(bot, update):
#     print('Hui start')
#     while True:
#         pass
#         get_emp_with_salary_lt = db.query("SELECT message FROM reminder WHERE notify_at > now()")
#
#         print(get_emp_with_salary_lt)
#         sleep(2)
#
#
# def main():
#     try:
#         text_message_handler = MessageHandler(Filters.text, text_message)
#         start_command_handler = CommandHandler('start', starter)
#         tags_command_handler = CommandHandler('tags', send_tags)
#         image_command_handler = CommandHandler('image', send_album)
#         help_command_handler = CommandHandler('help', get_help_command_list)
#         set_command_handler = CommandHandler('set', set_notification)
#
#         dispatcher.add_handler(start_command_handler)
#         dispatcher.add_handler(tags_command_handler)
#         dispatcher.add_handler(image_command_handler)
#         dispatcher.add_handler(help_command_handler)
#         dispatcher.add_handler(set_command_handler)
#         dispatcher.add_handler(text_message_handler)
#         # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#
#         updater.start_polling(clean=True)
#
#         updater.idle()
#     except Exception as e:
#         print("type error: " + str(e))

#
# if __name__ == '__main__':
#     try:
#         main()
#     except KeyboardInterrupt:
#         exit()