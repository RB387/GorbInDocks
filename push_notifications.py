from run import bot, user_data

def notification(user, type_message, users, file_name=''):
    if type_message == 'user': text = 'New user: {}'.format(user)
    elif type_message == 'file': text = 'New file: {}\nby user: {}'.format(file_name, user)
    else: return 0
    for admin in users:
        chat_id = user_data.get(admin)
        if chat_id:
            bot.send_message(chat_id, text)