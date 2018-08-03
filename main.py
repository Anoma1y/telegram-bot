import methods


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
