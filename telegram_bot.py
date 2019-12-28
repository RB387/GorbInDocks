import telebot
from application import app
from config import BOT_TOKEN
from run import bot
from get_stats import get_stats

@bot.message_handler(commands=['stats'])
def start_message(message):
    with app.app_context():
        data = get_stats()
    print(data)
    text = message.text.split()
    reply = ''
    if len(text)>1:
        user_stats = data['users'].get(text[-1])
        if user_stats:
            for line in user_stats.items():
                reply += ' : '.join(list(map(str, line))) + '\n'
        else:
            reply = 'User was not found'
    else:
        for line in data['overall'].items():
            reply += ' : '.join(list(map(str, line))) + '\n'
    bot.send_message(message.chat.id, reply)

def run():
    print('run')
    bot.polling()