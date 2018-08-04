import methods
from time import sleep
# import postgresql
# import config as CONFIG
# db = postgresql.open('pq://' + CONFIG.DB_USERNAME + ':' + CONFIG.DB_PASSWORD + '@' + CONFIG.DB_HOST + ':' + str(CONFIG.DB_PORT) + '/' + CONFIG.DB_NAME)


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


def get_last_commands():
    last_result = get_last_update_result()
    text = last_result['message']['text']
    return text


# invalid command
def invalid_cmd(chat_id, command):
    msg = 'Команда ' + command + ' не найдена\n'
    msg += 'Для получения списка доступных команд, напишите /help'
    methods.send_message(chat_id, msg)


# get command list
def get_help_command_list(chat_id):
    file = open("telegram_help.txt", 'r', encoding='utf-8')
    help_doc = ''
    if file.mode == 'r':
        help_doc = file.read().encode('UTF-8')
    methods.send_message(chat_id, help_doc)


# handler command
def handle_cmd(command):
    chat_id = get_last_chat_id()

    if command == '/start':
        methods.send_message(chat_id, 'Hello World')
    elif command == '/close':
        methods.send_message(chat_id, 'Closing the Telegram Bot')
    elif command == '/image':
        methods.send_photo(chat_id, 'http://image.noelshack.com/fichiers/2015/33/1439306897-169413-jpg.jpeg')
    elif command == '/help':
        get_help_command_list(chat_id)
    else:
        invalid_cmd(chat_id, command)


# invalid_cmd(get_last_chat_id(), '/fuck')
# get_help_command_list(get_last_chat_id())




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
#         sleep(2)
#
#
# if __name__ == '__main__':
#     try:
#         main()
#     except KeyboardInterrupt:
#         exit()
