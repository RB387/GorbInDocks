import telebot
from config import BOT_TOKEN
from run import bot

@bot.message_handler(content_types=['text'])
def start_message(message):
    bot.send_message(message.chat.id, 'works')

def run():
    print('run')
    bot.polling()