from application import app
from run import bot, open_config, dump, user_data
from config import TELEGRAM_PATH
from get_stats import get_stats
import json
import os

def get_reply(reply, items):
    for line in items:
        reply += ' : '.join(list(map(str, line))) + '\n'
    return reply

@bot.message_handler(commands=['stats'])
def send_stats(message):
    with app.app_context():
        data = get_stats()
    text = message.text.split()
    reply = ''
    if len(text)>1:
        user_stats = data['users'].get(text[-1])
        if user_stats:
            reply = get_reply(reply, user_stats.items())
        else:
            reply = 'User was not found'
    else:
        reply = get_reply(reply, data['overall'].items())
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=['start'])
def new_user(message):
    user_data.update({message.from_user.username : message.chat.id})
    dump(TELEGRAM_PATH, user_data)
    bot.send_message(message.chat.id, 'Registration succesfully!')

def run():
    print(' * Running Telegram bot')
    bot.polling()