from application import app
from run import bot, open_config, dump, user_data
from config import TELEGRAM_PATH
from get_stats import get_stats
from gorbin_tools2 import time2stamp, stamp2str
import datetime as dt
import json
import telebot
import os

message_history = {}

def get_reply(reply, items):
    '''Generate reply message'''
    for line in items:
        reply += ' : '.join(list(map(str, line))) + '\n'
    return reply

def get_date_keyboard(chat_id):
    '''Generate keyboard'''
    keyboard = telebot.types.InlineKeyboardMarkup()  
    keyboard.row(
        telebot.types.InlineKeyboardButton('Add begin date ({})'.format(message_history[chat_id]['begin-date']), callback_data='add-date-begin'),
        telebot.types.InlineKeyboardButton('Add end date ({})'.format(message_history[chat_id]['end-date']), callback_data='add-date-end'),
        telebot.types.InlineKeyboardButton('View stats', callback_data='add-date-view'),
    )
    return keyboard

def format_dates(date):
    '''Format dates to stamp'''
    if date in ['inf', '-inf']:
        return float(date)
    else:
        return time2stamp(date, pattern='%d.%m.%Y')
           
@bot.callback_query_handler(func=lambda call: True)  
def iq_callback(query):
    '''Keyboard input'''
    # get data
    data = query.data
    # if there is no info about user in history
    if query.message.chat.id not in message_history.keys():
        bot.send_message(query.message.chat.id, 'Error!')
        return
    # filter choice
    if data.startswith('filters-'): 
        # remove loading
        bot.answer_callback_query(query.id)
        # if user chose no filter
        if data == 'filters-None':
            keyboard = None
            # get stats
            with app.app_context():
                users_data = get_stats()
            # check if request got optional args
            user = message_history[query.message.chat.id].get('user')
            if user:
                # if it is, get user data
                user_data = users_data['users'].get(user)
                if user_data:
                    # if such user exists then get info about his activity
                    reply = get_reply('', users_data['users'][user].items())
                else:
                    # else send error
                    reply = 'User was not found'
            else:
                # if no optional args, then send all data
                reply = get_reply('', users_data['overall'].items())
        elif data == 'filters-Add':
            # if user chose filters
            reply = 'Choose filters:'
            # send him keyboard with options
            keyboard = get_date_keyboard(query.message.chat.id)
            
    elif data.startswith('add-date'):
        keyboard = None
        if data == 'add-date-begin':
            # if user inputs date begin
            # update his status
            message_history[query.message.chat.id].update({'status': 'add-begin'})
            reply =  'Enter begin date in format dd.mm.year: '
        elif data == 'add-date-end':
            # if user inputs date end
            # update his status
            message_history[query.message.chat.id].update({'status': 'add-end'})
            reply = 'Enter end date in formart dd.mm.year'
        elif data == 'add-date-view':
            # if user wants to view stats
            # get begin and end dates
            begin = format_dates(message_history[query.message.chat.id]['begin-date'])
            end = format_dates(message_history[query.message.chat.id]['end-date'])
            # get stats from begin date to end date
            with app.app_context():
                users_data = get_stats(date_begin=begin, date_end=end)
            # check if request got optional args
            user = message_history[query.message.chat.id].get('user')
            # if it is
            if user:
                # check if such user exists
                user_data = users_data['users'].get(user)
                if user_data:
                    # if such user exists then get info about his activity
                    reply = get_reply('', users_data['users'][user].items())
                else:
                    # else send error
                    reply = 'User was not found'
            else:
                # if no args, send overall stats
                reply = get_reply('', users_data['overall'].items())
    # send msg
    bot.send_message(query.message.chat.id, reply, reply_markup=keyboard)

@bot.message_handler(func=lambda message: (message_history.get(message.chat.id) and
((message_history.get(message.chat.id).get('status') == 'add-begin') or (message_history.get(message.chat.id).get('status') == 'add-end'))), 
content_types=['text'])
def get_begin_date(message):
    '''User date input'''
    try:
        # Try to convert to check if date is correct
        if message.text not in ['inf', '-inf']:
            dt.datetime.strptime(message.text, '%d.%m.%Y')
    except:
        # else send error
        bot.send_message(message.chat.id, 'Invalid date!')
        return
    # get info about what to rewrite
    if message_history[message.chat.id]['status'] == 'add-begin':
        action = 'begin-date'
    else:
        action = 'end-date'
    # update date and status
    message_history[message.chat.id].update({action: message.text})
    message_history[message.chat.id].update({'status': 'None'})
    # gen keyboard
    keyboard = get_date_keyboard(message.chat.id)
    # send msg
    bot.send_message(message.chat.id, 'Added succesfully!', reply_markup=keyboard)

@bot.message_handler(commands=['stats'])
def send_stats(message):
    '''/stats command menu

        optional args:
        user_login -- which user stats admin wants to see

    '''
    # Split message to get optional args
    text = message.text.split()
    # Create user's data in message history
    message_history.update({message.chat.id: {'status': 'filter-decision'}})
    message_history[message.chat.id].update({'begin-date': "-inf"})
    message_history[message.chat.id].update({'end-date': "inf"})
    # if there is args
    if len(text)>1:
        # save it
        message_history[message.chat.id].update({'user': text[-1]})
    # generate keyboard
    keyboard = telebot.types.InlineKeyboardMarkup()  
    keyboard.row(  
        telebot.types.InlineKeyboardButton('No', callback_data='filters-None'),
        telebot.types.InlineKeyboardButton('Yes', callback_data='filters-Add')    
    )
    # send msg
    bot.send_message(message.chat.id, 'Add filters?', reply_markup=keyboard)

@bot.message_handler(commands=['help'])
def help_info(message):
    '''/help command menu'''
    reply = ('Available commands:\n'+
            '/stats - get stats of users activity\n'+
            'Optional arguments -- user_login\n'+
            '/stats user_login')
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=['start'])
def new_user(message):
    '''Function for user registration
        runs when user send /start message
    '''
    # Update dict (Telegram username: Telegram chat id)
    user_data.update({message.from_user.username : message.chat.id})
    # Dump to JSON config
    dump(TELEGRAM_PATH, user_data)
    bot.send_message(message.chat.id, 'Registrated succesfully!')

def run():
    '''Function to run bot'''
    print(' * Running Telegram bot')
    bot.polling()