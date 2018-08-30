#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import config as CONFIG
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, run_async
from time import sleep
import datetime
from Modules import yandere
from Modules.reminder import Reminder
from Modules.dictionary import Dictionary
from Db.reminder import ReminderQueries
import psycopg2

unix_time = {
    'minute': 60,
    'hour': 3600,
    'day': 86400,
    'week': 604800,
    'month': 2629743,
    'year': 31556926
}
UPDATE_TIME = 30

DB_CONNECT = psycopg2.connect(
    host=CONFIG.DB_HOST,
    user=CONFIG.DB_USERNAME,
    password=CONFIG.DB_PASSWORD,
    database=CONFIG.DB_NAME,
    port=CONFIG.DB_PORT
)


# get command list
def get_help_command_list(bot, update):
    help_doc = 'Список доступных команд:\n'
    help_doc += '\t\t/image {имя тега} - Получить последние картинки за 1 неделю, {имя тега} - картинки по тегу\n'
    help_doc += '\t\t/tags {имя тега} - Получить все популярные теги, {имя тега} - поиск по тегу\n'
    help_doc += '\t\t/addword {english} {russian}- Добавить слово в словарик, ' \
                '{english} - слово на английском, {russian} - перевод слова, через запятую\n'
    help_doc += '\t\t/getwords - Получить рандомный список слов'
    help_doc += '\t\t/help - Список команд\n'
    bot.sendMessage(chat_id=update.message.chat_id, text=help_doc)


def get_params_cmd(update):
    cmd = update.message.text.split(' ', maxsplit=1)

    if len(cmd) <= 1:
        param = ''
    else:
        param = cmd[1]

    return param


def send_album(bot, update):
    chat_id = update.message.chat_id
    tags = get_params_cmd(update)

    json_data = yandere.get_images(
        page_limit=3,
        tags=tags,
        period_time=unix_time['week'],
        limit=5
    )

    if len(json_data) == 0:
        bot.sendMessage(chat_id=chat_id, text='Изображения не найдены')

    for data in json_data:
        bot.sendPhoto(chat_id=chat_id, photo=data['file_url'])


def send_tags(bot, update):
    chat_id = update.message.chat_id
    tag_name = get_params_cmd(update)

    tags_list = yandere.get_available_tags(tag_name)

    if len(tags_list) > 0:
        bot.sendMessage(chat_id=chat_id, text=tags_list)
    else:
        bot.sendMessage(chat_id=chat_id, text='Теги не найдены')


def check_reminder(msg):
    remind_word = 'напомни мне'
    msg = re.sub('\s+', ' ', msg)

    if re.search(remind_word, msg.lower()) or re.search('^что\s', msg.strip()):
        return True

    return False


def delta_time(f_t):
    c_t = datetime.datetime.now()
    return f_t - c_t


def parse_delta_time(d):
    return [
        d.days,
        d.seconds // 3600,
        (d.seconds//60) % 60
    ]


def delta_time_to_minutes(d):
    days = d.days
    hours = d.seconds // 3600
    minutes = (d.seconds // 60) % 60

    if hours != 0:
        minutes += (hours * 60)

    if days != 0:
        minutes += (days * 24 * 60)

    return minutes


# todo перенести в reminder.py
def pre_reminder(remind_id, minutes):
    rem = []
    c_t = datetime.datetime.now()
    pre_remind_breakpoint = [10, 30, 60, 360, 1440, 2880, 10080, 21600, 43200]

    for pr in pre_remind_breakpoint:
        if minutes > pr:
            new_date = c_t + datetime.timedelta(minutes=pr)
            rem.append((remind_id, new_date))

    return rem


@run_async
def text_message(bot, update):
    text = update.message.text
    chat_id = update.message.chat_id

    if check_reminder(text):
        try:
            reminder = Reminder(msg=text)
            (msg, notify_at) = reminder.start()
            notify_at.strftime("%Y-%m-%d %H:%M:%S")

            query = ReminderQueries(db=DB_CONNECT)
            reminder_response = query.insert_remind(
                user_id=chat_id,
                msg=msg,
                time=notify_at
            )

            delta = delta_time(notify_at)
            minutes = delta_time_to_minutes(delta)

            pre_rem = pre_reminder(
                remind_id=reminder_response['data'][0],
                minutes=minutes
            )

            pre_reminder_response = query.insert_pre_reminder(pre_rem)

            if reminder_response['status'] and pre_reminder_response['status']:
                bot.send_message(chat_id=chat_id, text="Напоминание '{message}' создано".format(
                    message=reminder_response['data'][2]
                ))

            else:
                bot.send_message(chat_id=chat_id, text=reminder_response['data'])

        except Exception as err:
            err = str(err)
            bot.send_message(chat_id=chat_id, text=err)

    else:
        bot.send_message(chat_id=chat_id, text=text)


@run_async
def add_word(bot, update):
    text = update.message.text
    chat_id = update.message.chat_id

    dict = Dictionary(language='english', db=DB_CONNECT)
    response = dict.insert(text)

    if response['status']:
        bot.send_message(chat_id=chat_id, text='Слово {response_text} успешно добавлено'.format(
            response_text=response['data'][1]
        ))

    else:
        bot.send_message(chat_id=chat_id, text=response['data'])


@run_async
def get_word(bot, update):
    text = ' '.join(update.message.text.split()[1:])
    chat_id = update.message.chat_id

    dict = Dictionary(language='english', db=DB_CONNECT)
    response = dict.get_by_word(text)

    result = ''
    for w in response:
        result += '{word} - {translate}\n'.format(
            word=w[1],
            translate=w[2]
        )

    if len(response) != 0:
        bot.send_message(chat_id=chat_id, text=result)
        return

    bot.send_message(chat_id=chat_id, text='Слово не найдено')


@run_async
def get_random_list(bot, update):
    chat_id = update.message.chat_id

    dict = Dictionary(language='english', db=DB_CONNECT)
    response = dict.get_random_list()
    text = ''

    for res in response:
        text += '{word} - {translate}\n'.format(
            word=res[1],
            translate=res[2],
        )

    bot.send_message(chat_id=chat_id, text=text)


updater = Updater(token=CONFIG.TOKEN)
dispatcher = updater.dispatcher


class Ping:

    def __init__(self):
        self.is_started = True

    @run_async
    def start(self):
        self.is_started = True
        while self.is_started:
            query = ReminderQueries(db=DB_CONNECT)
            response = query.get_remind_upcoming()

            if len(response) > 0:
                self.handle_reminder(response)

            sleep(5)
        return

    def stop(self):
        self.is_started = False
        return

    def handle_reminder(self, notifies):
        for notify in notifies:
            notify_id = notify[0]
            user_id = notify[1]
            message = notify[2]
            notify_at = notify[3]
            c_t = datetime.datetime.now()
            delta = notify_at - c_t
            minutes = (delta.seconds % 3600) // 60

            query = ReminderQueries(db=DB_CONNECT)
            query.update_pre_remind(notify_id)

            text_remind = ''
            text_remind += 'Напоминание: {message}\n'.format(message=message)
            text_remind += 'Время: через {minutes} минут'.format(minutes=minutes)

            dispatcher.bot.sendMessage(chat_id=user_id, text=text_remind)


def main():
    try:
        bot = Ping()
        bot.start()
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        text_message_handler = MessageHandler(Filters.text, text_message)
        tags_command_handler = CommandHandler('tags', send_tags)
        image_command_handler = CommandHandler('image', send_album)
        help_command_handler = CommandHandler('help', get_help_command_list)
        addword_command_handler = CommandHandler('addword', add_word)
        getword_command_handler = CommandHandler('getword', get_word)
        getrandomwords_command_handler = CommandHandler('getwords', get_random_list)

        dispatcher.add_handler(tags_command_handler)
        dispatcher.add_handler(image_command_handler)
        dispatcher.add_handler(help_command_handler)
        dispatcher.add_handler(addword_command_handler)
        dispatcher.add_handler(text_message_handler)
        dispatcher.add_handler(getword_command_handler)
        dispatcher.add_handler(getrandomwords_command_handler)

        updater.start_polling(clean=True)

        updater.idle()
    except Exception as e:
        print("type error: " + str(e))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
