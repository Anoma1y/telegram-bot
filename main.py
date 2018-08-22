#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import config as CONFIG
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, run_async
from time import sleep
from Modules import yandere
from Modules.reminder import Reminder
from Modules.dictionary import Dictionary
from Db.reminder import ReminderQueries

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


@run_async
def text_message(bot, update):
    text = update.message.text
    chat_id = update.message.chat_id

    if check_reminder(text):
        try:
            reminder = Reminder(msg=text)
            (msg, notify_at) = reminder.start()
            notify_at.strftime("%Y-%m-%d %H:%M:%S")

            query = ReminderQueries()
            response = query.insert_remind(
                user_id=chat_id,
                msg=msg,
                time=notify_at
            )

            if response['status']:
                bot.send_message(chat_id=chat_id, text="Напоминание '{message}' создано".format(
                    message=response['data'][2]
                ))
            else:
                bot.send_message(chat_id=chat_id, text=response['data'])

        except Exception as err:
            err = str(err)
            bot.send_message(chat_id=chat_id, text=err)

    else:
        bot.send_message(chat_id=chat_id, text=text)


@run_async
def add_word(bot, update):
    text = update.message.text
    chat_id = update.message.chat_id

    dict = Dictionary(language='english')
    response = dict.insert(text)

    if response['status']:
        bot.send_message(chat_id=chat_id, text='Слово {response_text} успешно добавлено'.format(
            response_text=response['data'][1]
        ))
    else:
        bot.send_message(chat_id=chat_id, text=response['data'])


updater = Updater(token=CONFIG.TOKEN)
dispatcher = updater.dispatcher


class Bot:

    def __init__(self):
        self.is_started = True

    @run_async
    def start(self):
        self.is_started = True
        while self.is_started:
            query = ReminderQueries()
            response = query.get_remind_upcoming()

            sleep(10)
        return

    def stop(self):
        self.is_started = False
        return


def main():
    try:
        bot = Bot()
        bot.start()
        text_message_handler = MessageHandler(Filters.text, text_message)
        tags_command_handler = CommandHandler('tags', send_tags)
        image_command_handler = CommandHandler('image', send_album)
        help_command_handler = CommandHandler('help', get_help_command_list)
        addword_command_handler = CommandHandler('addword', add_word)

        dispatcher.add_handler(tags_command_handler)
        dispatcher.add_handler(image_command_handler)
        dispatcher.add_handler(help_command_handler)
        dispatcher.add_handler(addword_command_handler)
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